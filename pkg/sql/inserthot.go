package sql

import (
	"context"
	"fmt"
	// "sync"

	// "github.com/cockroachdb/cockroach/pkg/sql/pgwire/pgcode"
	// "github.com/cockroachdb/cockroach/pkg/sql/pgwire/pgerror"
	// "github.com/cockroachdb/cockroach/pkg/sql/privilege"
	// "github.com/cockroachdb/cockroach/pkg/sql/row"
	// "github.com/cockroachdb/cockroach/pkg/sql/rowcontainer"
	"github.com/cockroachdb/cockroach/pkg/sql/sem/tree"
	// "github.com/cockroachdb/cockroach/pkg/sql/sqlbase"
	"github.com/cockroachdb/cockroach/pkg/sql/types"
	// "github.com/cockroachdb/cockroach/pkg/util/errorutil/unimplemented"
	// "github.com/cockroachdb/cockroach/pkg/util/tracing"
)

func (p *planner) InsertHot(
	ctx context.Context, n *tree.InsertHot, desiredTypes []*types.T,
) (result planNode, resultErr error) {
	return nil, fmt.Errorf("jenndebug we're not quite inserting hot yet...")
}
