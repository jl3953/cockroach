package tree

// InsertHot represents an the hot version of Insert
type InsertHot struct {
	With		*With
	Table		TableExpr
	Columns		NameList
	Rows		*Select
	OnConflict	*OnConflictHot
	Returning	ReturningClause
}

// Format imlpements the NodeFormatter interface
func (node *InsertHot) Format(ctx *FmtCtx) {
	ctx.FormatNode(node.With)
	if node.OnConflict.IsUpsertAlias() {
		ctx.WriteString("UPSERTHOT")
	} else {
		ctx.WriteString("INSERTHOT")
	}

	ctx.WriteString(" INTO ")
	ctx.FormatNode(node.Table)
	if node.Columns != nil {
		ctx.WriteByte('(')
		ctx.FormatNode(&node.Columns)
		ctx.WriteByte(')')
	}
	if node.DefaultValues() {
		ctx.WriteString(" DEFAULT VALUES")
	} else {
		ctx.WriteByte(' ')
		ctx.FormatNode(node.Rows)
	}
	if node.OnConflict != nil && !node.OnConflict.IsUpsertAlias() {
		ctx.WriteString(" ON CONFLICT ")
		if len(node.OnConflict.Columns) > 0 {
			ctx.WriteString(" (")
			ctx.FormatNode(&node.OnConflict.Columns)
			ctx.WriteString(")")
		}
		if node.OnConflict.DoNothing {
			ctx.WriteString(" DO NOTHING")
		} else {
			ctx.WriteString(" DO UPDATE SET ")
			ctx.FormatNode(&node.OnConflict.Exprs)
			if node.OnConflict.Where != nil {
				ctx.WriteByte(' ')
				ctx.FormatNode(node.OnConflict.Where)
			}
		}
	}
	if HasReturningClause(node.Returning) {
		ctx.WriteByte(' ')
		ctx.FormatNode(node.Returning)
	}
}

// Default Values returns true iff only default values are being inserted.
func (node *InsertHot) DefaultValues() bool {
	return node.Rows.Select == nil
}

// OnConflictHot represents an `ON CONFLICT (columns) DO UPDATE SET exprs WHERE
// where` clause.
//
// The zero value for OnConflictHot is used to signal the UPSERT short form, which
// uses the primary key for as the conflict index and the values being inserted
// for Exprs.
type OnConflictHot struct {
	Columns		NameList
	Exprs		UpdateExprs
	Where		*Where
	DoNothing	bool
}

// IsUpsertAlias returns true if the UPSERT syntactic sugar was used.
func (oc *OnConflictHot) IsUpsertAlias() bool {
	return oc != nil && oc.Columns == nil && oc.Exprs == nil && oc.Where == nil && !oc.DoNothing
}
