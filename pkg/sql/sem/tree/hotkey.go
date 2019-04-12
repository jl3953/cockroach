package tree

type HotKey struct {
	// Only one of Table and Index can be set.
	Table *TableName
	Index *TableIndexName
	// Each row contains values for the columns in the PK or index (or a prefix
	// of the columns).
	Rows *Select
}

// Format implements the NodeFormatter interface.
func (node *HotKey) Format(ctx *FmtCtx) {
	ctx.WriteString("ALTER TABLE ")
	ctx.FormatNode(node.Table)
	ctx.WriteString(" SPLIT AT ")
	ctx.FormatNode(node.Rows)
}
