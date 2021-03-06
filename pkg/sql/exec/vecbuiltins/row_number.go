// Copyright 2019 The Cockroach Authors.
//
// Use of this software is governed by the Business Source License
// included in the file licenses/BSL.txt.
//
// As of the Change Date specified in that file, in accordance with
// the Business Source License, use of this software will be governed
// by the Apache License, Version 2.0, included in the file
// licenses/APL.txt.

package vecbuiltins

import "github.com/cockroachdb/cockroach/pkg/sql/exec"

// TODO(yuzefovich): add benchmarks.

// NewRowNumberOperator creates a new exec.Operator that computes window
// function ROW_NUMBER. outputColIdx specifies in which exec.Vec the operator
// should put its output (if there is no such column, a new column is
// appended).
func NewRowNumberOperator(
	input exec.Operator, outputColIdx int, partitionColIdx int,
) exec.Operator {
	base := rowNumberBase{
		OneInputNode:    exec.NewOneInputNode(input),
		outputColIdx:    outputColIdx,
		partitionColIdx: partitionColIdx,
	}
	if partitionColIdx == -1 {
		return &rowNumberNoPartitionOp{base}
	}
	return &rowNumberWithPartitionOp{base}
}

// rowNumberBase extracts common fields and common initialization of two
// variations of row number operators. Note that it is not an operator itself
// and should not be used directly.
type rowNumberBase struct {
	exec.OneInputNode
	outputColIdx    int
	partitionColIdx int

	rowNumber int64
}

func (r *rowNumberBase) Init() {
	r.Input().Init()
}
