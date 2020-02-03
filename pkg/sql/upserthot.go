package sql

import (
	"context"
	"sync"

	"github.com/cockroachdb/cockroach/pkg/sql/pgwire/pgcode"
	"github.com/cockroachdb/cockroach/pkg/sql/pgwire/pgerror"
	"github.com/cockroachdb/cockroach/pkg/sql/row"
	"github.com/cockroachdb/cockroach/pkg/sql/sem/tree"
	"github.com/cockroachdb/cockroach/pkg/sql/sqlbase"
	"github.com/cockroachdb/cockroach/pkg/sql/types"
	"github.com/cockroachdb/cockroach/pkg/util"
	"github.com/cockroachdb/cockroach/pkg/util/errorutil/unimplemented"
	"github.com/cockroachdb/cockroach/pkg/util/tracing"
	"github.com/cockroachdb/cockroach/pkg/util/log"
)

func (p *planner) newUpsertHotNode(
		ctx context.Context,
		n *tree.Insert,
		desc *sqlbase.ImmutableTableDescriptor,
		ri row.Inserter,
		tn, alias *tree.TableName,
		sourceRows planNode,
		needRows bool,
		resultcols sqlbase.ResultColumns,
		defaultExprs []tree.TypedExpr,
		computeExprs []tree.TypedExpr,
		computedCols []sqlbase.ColumnDescriptor,
		fkTables row.FkTableMetadata,
		desiredTypes []*types.T,
) (res batchedPlanNode, err error) {
	// Extract the index that will detect upsert conflicts
	// (conflictIndex)
}
