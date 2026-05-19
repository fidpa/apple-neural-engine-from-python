#!/usr/bin/env python3
"""
Inspect the BERTSQUADFP16 model to understand its exact requirements.

Dumps the CoreML spec (input/output names, dtypes, shapes) and then probes
which dtype/shape combinations the model actually accepts — this is how the
undocumented input contract (float64, [1, 384], wordIDs/wordTypes) was found.
"""

import sys

import numpy as np
from coremltools.models import MLModel


def main() -> int:
    """Print the model spec, then probe input dtype/shape acceptance.

    Returns:
        0 — informational tool, always succeeds if the model loads.
    """
    print("Loading model...")
    model = MLModel('BERTSQUADFP16.mlmodel')
    spec = model.get_spec()

    print("\n" + "="*60)
    print("MODEL SPECIFICATION DETAILS")
    print("="*60)

    # Get detailed input specifications
    print("\n📥 INPUT SPECIFICATIONS:")
    for i, input_spec in enumerate(spec.description.input):
        print(f"\nInput {i+1}: '{input_spec.name}'")
        print(f"  Type: {input_spec.type}")

        if input_spec.type.HasField('multiArrayType'):
            arr_type = input_spec.type.multiArrayType
            print(f"  Data Type: {arr_type.dataType}")
            print(f"  Shape: {list(arr_type.shape)}")

            # Check for flexible shapes
            if arr_type.HasField('shapeRange'):
                print("  Shape Range:")
                for j, dim in enumerate(arr_type.shapeRange.sizeRanges):
                    print(f"    Dim {j}: [{dim.lowerBound}, {dim.upperBound}]")

    # Get output specifications
    print("\n📤 OUTPUT SPECIFICATIONS:")
    for i, output_spec in enumerate(spec.description.output):
        print(f"\nOutput {i+1}: '{output_spec.name}'")
        print(f"  Type: {output_spec.type}")

        if output_spec.type.HasField('multiArrayType'):
            arr_type = output_spec.type.multiArrayType
            print(f"  Data Type: {arr_type.dataType}")
            print(f"  Shape: {list(arr_type.shape)}")

    # Test with minimal inputs
    print("\n" + "="*60)
    print("TESTING MINIMAL INPUTS")
    print("="*60)

    # Create test inputs with different shapes and types
    test_inputs: list[dict[str, object]] = [
        # Test 1: Simple 1D array as list
        {
            'wordIDs': [101, 2003, 102],
            'wordTypes': [0, 0, 0]
        },
        # Test 2: 2D array as nested list
        {
            'wordIDs': [[101, 2003, 102]],
            'wordTypes': [[0, 0, 0]]
        },
        # Test 3: numpy int32 arrays
        {
            'wordIDs': np.array([[101, 2003, 102]], dtype=np.int32),
            'wordTypes': np.array([[0, 0, 0]], dtype=np.int32)
        },
        # Test 4: numpy float32 arrays
        {
            'wordIDs': np.array([[101, 2003, 102]], dtype=np.float32),
            'wordTypes': np.array([[0, 0, 0]], dtype=np.float32)
        },
        # Test 5: numpy int64 arrays
        {
            'wordIDs': np.array([[101, 2003, 102]], dtype=np.int64),
            'wordTypes': np.array([[0, 0, 0]], dtype=np.int64)
        }
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}:")
        print(f"  Input types: wordIDs={type(test_input['wordIDs'])}, "
              f"wordTypes={type(test_input['wordTypes'])}")

        if isinstance(test_input['wordIDs'], np.ndarray):
            print(f"  Array dtypes: wordIDs={test_input['wordIDs'].dtype}, "
                  f"wordTypes={test_input['wordTypes'].dtype}")
            print(f"  Array shapes: wordIDs={test_input['wordIDs'].shape}, "
                  f"wordTypes={test_input['wordTypes'].shape}")

        try:
            result = model.predict(test_input)
            print(f"  ✅ SUCCESS! Output keys: {list(result.keys())}")

            if 'startLogits' in result:
                print(f"     startLogits shape: {result['startLogits'].shape}")
            if 'endLogits' in result:
                print(f"     endLogits shape: {result['endLogits'].shape}")

        except Exception as exc:  # noqa: BLE001 — probe: every combo must be tried
            print(f"  ❌ FAILED: {str(exc)[:200]}")

    print("\n" + "="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
