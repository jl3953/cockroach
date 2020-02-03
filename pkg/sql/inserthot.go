package sql

import (
	"context"
	// "fmt"
	// "sync"

	// "github.com/cockroachdb/cockroach/pkg/sql/pgwire/pgcode"
	// "github.com/cockroachdb/cockroach/pkg/sql/pgwire/pgerror"
	"github.com/cockroachdb/cockroach/pkg/sql/privilege"
	"github.com/cockroachdb/cockroach/pkg/sql/row"
	// "github.com/cockroachdb/cockroach/pkg/sql/rowcontainer"
	"github.com/cockroachdb/cockroach/pkg/sql/sem/tree"
	"github.com/cockroachdb/cockroach/pkg/sql/sqlbase"
	"github.com/cockroachdb/cockroach/pkg/sql/types"
	// "github.com/cockroachdb/cockroach/pkg/util/errorutil/unimplemented"
	"github.com/cockroachdb/cockroach/pkg/util/tracing"
)

func (p *planner) InsertHot(
	ctx context.Context, n *tree.InsertHot, desiredTypes []*types.T,
) (result planNode, resultErr error) {

	// CTE analysis jenndebug mayberemove
	resetter, err := p.initWith(ctx, n.With)
	if err != nil {
		return nil, err
	}

	if resetter != nil {
		defer func() {
			if cteErr := resetter(p); cteErr != nil && resultErr == nil {
				// If no error was found in the inner planning but a CTE error
				// is ocurring during the final checks on the way back from
				// the recursion, use that error as final error for this
				// stage.
				resultErr = cteErr
				result = nil
			}
		}()
	}

	tracing.AnnotateTrace()

	// INSERT INTO xx AS yy - we want to know about xx (tn) because
	// that's what we get the descriptor with, and yy (alias) because
	// that's what RETURNING will use
	tn, alias, err := p.getAliasedTableName(n.Table)
	if err != nil {
		return nil, err
	}

	// Find which table we're working on, check the permissions
	desc, err := ResolveExistingObject(ctx, p, tn, tree.ObjectLookupFlagsWithRequired(), ResolveRequireTableDesc)
	if err != nil {
		return  nil, err
	}
	if err := p.CheckPrivilege(ctx, desc, privilege.INSERT); err != nil {
		return nil, err
	}
	if !n.OnConflict.DoNothing {
		// UPSERT and INDEX ON CONFLICT will read from the table to check for duplicates.
		if err := p.CheckPrivilege(ctx, desc, privilege.SELECT); err != nil {
			return nil, err
		}
		if !n.OnConflict.DoNothing {
			// UPSERT and INDEX ON CONFLICT DO UPDATE may modify rows.
			if err := p.CheckPrivilege(ctx, desc, privilege.UPDATE); err != nil {
				return nil, err
			}
		}
	}

	// Set up any check constraints
	checkHelper, err := sqlbase.NewEvalCheckHelper(ctx, p.analyzeExpr, desc)
	if err != nil {
		return nil, err
	}

	// Determine what are the foreign key tables that are involved in the update
	var fkCheckType row.FKCheckType
	if n.OnConflict == nil || n.OnConflict.DoNothing {
		fkCheckType = row.CheckInserts
	} else {
		fkCheckType = row.CheckUpdates
	}
	fkTables, err := row.MakeFkMetadata(
			ctx,
			desc,
			fkCheckType,
			p.LookupTableByID,
			p.CheckPrivilege,
			p.analyzeExpr,
			checkHelper,
		)
	if err != nil {
		return nil, err
	}

	// Determine which columns we're inserting into
	var insertCols []sqlbase.ColumnDescriptor
	if n.DefaultValues() {
		// No target column, select all columns in the table, including
		// hidden columns; these may have defaults too.
		//
		// Although this races with the backfill in case of UPSERT we do
		// not care: the backfill is also inserting defaults, and we do
		// not provide guarantees about the evaluation order of default
		// expressions.
		insertCols = desc.WritableColumns()
	} else {
		var err error
		if insertCols, err = sqlbase.ProcessTargetColumns(desc, n.Columns,
				true /* ensureColumns */, false /* allowMutations */); err != nil {
			return nil, err
		}
	}

	// maxInsertIdx is the highest column index we are allowed to insert into -
	// in the presence of computed columns, when we don't explicitly specify the
	// columns we're inserting into, we should allow inserts if and only if they
	// don't touch a computed columns, and we only have the ordinal positions to
	// go by.
	maxInsertIdx := len(insertCols)
	for i, col := range insertCols {
		if col.IsComputed() {
			maxInsertIdx = i
			break
		}
	}

	// Number of columns expecting an input. This doesn't include the
	// columns receiving a default value, or computed columns.
	numInputColumns := len(insertCols)

	// We update the set of columns being inserted into with any computed columns.
	insertCols, computedCols, computeExprs, err :=
		sqlbase.ProcessComputedColumns(ctx, insertCols, tn, desc, &p.txCtx, p.EvalContext())
	if err != nil {
		return nil, err
	}

	// We update the set of columns being inserted into with any default values
	// for columns. This needs to happen after we process the computed columns,
	// because `defaultExprs` is expected to line up with the final set of
	// columns being inserted into.
	insertCols, defaultExprs, err :=
		sqlbase.ProcessDefaultColumns(insertCols, desc, &p.txCtx, p.EvalContext())
	if err != nil {
		return nil, err
	}

	// Now create the source data plan. For this we need an AST and as
	// list of required types. The AST comes from the Rows operand, the
	// required types from the inserted columns.

	// Analyze the expressions for column information and typing.
	requiredTypesFromSelect := make([]*types.T, len(insertCols))
	for i := range insertCols {
		requiredTypesFromSelect[i] = &insertCols[i].Type
	}

	// Extract the AST for the data source
	isUpsert := n.OnConflict.IsUpsertAlias()
	var insertRows tree.SelectStatement
	arityChecked := false
	colNames := make(tree.NameList, len(insertCols))
	for i := range insertCols {
		colNames[i] = tree.Name(insertCols[i].Name)
	}
	if n.DefaultValues() {
		insertRows = newDefaultValuesClause(defaultExprs, colNames)
	} else {
		src, values, err := extractInsertSource(colNames, n.Rows)
		if err != nil {
			return nil, err
		}
		if values != nil {
			if len(values.Rows) > 0 {
				// Check to make sure the values clause doesn't have too many or
				// too few expression in each tuple.
				numExprs := len(values.Rows[0])
				if err := checkNumExprs(isUpsert, numExprs, numInputColumns, n.Columns != nil); err != nil {
					return nil, err
				}
				if numExprs > maxInsertIdx {
					// TODO(justin): this is too restrictive. It should
					// be possible to allow INSERT INTO (x) VALUES (DEFAULT)
					// if x is a computed column. See #22434
					return nil, sqlbase.CannotWriteToComputedColError(insertCols[maxInsertIdx].Name)
				}
				arityChecked = true
			}
			src, err = fillDefaults(defaultExprs, insertCols, values)
			if err != nil {
				return nil, err
			}
		}
		insertRows = src
	}

	// Ready to create the plan for the data source; do it.
	// This performs type checking on source expressions, collecting
	// types for placeholders in the process.
	rows, err := p.newPlan(ctx, insertRows, requiredTypesFromSelect)
	if err != nil {
		return nil, err
	}

	srcCols := planColumns(rows)
	if !arityChecked {
		// If the insert source was not a VALUES clause, then we have not
		// already verified the arity of the operand is correct.
		// Do it now.
		numExprs := len(srcCols)
		if err := checkNumExprs(isUpsert, numExprs, numInputColumns, n.Columns != nil); err != nil {
			return nil, err
		}
		if numExprs > maxInsertIdx {
			return nil, sqlbase.CannotWriteToComputedColError(insertCols[maxInsertIdx].Name)
		}
	}

	// The required types may not have been matched exactly by the planning.
	// While this may be OK if the results were geared toward a client,
	// for INSERT/UPSERT we must have a direct match.
	for i, srcCol := range srcCols {
		if err := sqlbase.CheckDatumTypeFitsColumnType(&insertCols[i], srcCol.Typ); err != nil {
			return nil, err
		}
	}

	// Create the table insert, which does the bulk of the work.
	ri, err := row.MakeInserter(p.txn, desc, fkTables, insertCols,
			row.CheckFKs, &p.alloc)
	if err != nil {
		return nil, err
	}

	// rowsNeeded will help determine whether we need to allocate a
	// rowsContainer.
	rowsNeeded := resultsNeeded(n.Returning)

	// Determine the relational type of the generated insert node.
	// If rows are not needed, no columns are returned.
	var columns sqlbase.ResultColumns
	if rowsNeeded {
		columns = sqlbase.ResultColumnsFromColDescs(desc.Columns)
	}

	// Since all columns are being returned, use the 1:1 mapping.
	tabColIdxToRetIdx := make([]int, len(desc.Columns))
	for i := range tabColIdxToRetIdx {
		tabColIdxToRetIdx[i] = i
	}

	// At this point, everything is ready for either an insertNode or an upsertNode.

	var node batchedPlanNode

	if n.OnConflict != nil {
		// This is an UPSERT, or INSERT ... ON CONFLICT.
		// The upsert path has a separate constructor.
		node, err = p.newUpsertNode(
			ctx, n, desc, ri, tn, alias, rows, rowsNeeded, columns,
			defaultExprs, computeExprs, computedCols, fkTables, desiredTypes)
		if err != nil {
			return nil, err
		}
	} else {
		// Regular path for INSERT.
		in := insertNodePool.Get().(*insertNode)
		*in = insertNode{
			source: rows,
			columns: columns,
			run: insertRun {
				ti: tableInserter{ri: ri},
				checkHelper: checkHelper,
				rowsNeeded: rowsNeeded,
				computedCols: computedCols,
				computeExprs: computeExprs,
				iVarContainerForComputedCols: sqlbase.RowIndexedVarContainer{
					Cols: desc.Columns,
					Mapping: ri.InsertColIDtoRowIndex,
				},
				defaultExprs: defaultExprs,
				insertCols: ri.InsertCols,
				tabColIdxToRetIdx: tabColIdxToRetIdx,
			},
		}
		node = in
	}

	// Finally, handle RETURNING, if any.
	r, err := p.Returning(ctx, node, n.Returning, desiredTypes, alias)
	if err != nil {
		// We close explicitly here to release the node to the pool.
		node.Close(ctx)
	}
	return r, err
}
