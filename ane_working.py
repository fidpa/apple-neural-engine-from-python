#!/usr/bin/env python3
"""
Working Apple Neural Engine test for BERTSQUADFP16 model
Correctly handles the model's requirement for float64 arrays of shape [1, 384]
"""

import sys
import time

import coremltools
import numpy as np
from transformers import BertTokenizer


def pad_or_truncate(arr: list[float], target_length: int = 384) -> list[float]:
    """Pad with zeros or truncate a 1-D list to exactly target_length."""
    current_length = len(arr)
    if current_length > target_length:
        return arr[:target_length]
    elif current_length < target_length:
        # Pad with zeros
        padding = [0] * (target_length - current_length)
        return arr + padding
    return arr

def main() -> int:
    """Run the BERT-SQuAD question-answering demo on the ANE.

    Returns:
        0 if at least one inference succeeded, 1 otherwise.
    """
    print("="*60)
    print("🚀 Apple Neural Engine Test - M4 Pro")
    print("="*60)

    # Load model
    print("\n📦 Loading BERTSQUADFP16.mlmodel...")
    model = coremltools.models.MLModel('BERTSQUADFP16.mlmodel')
    print("✅ Model loaded successfully!")

    # Initialize tokenizer
    print("🔤 Initializing tokenizer...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # Test cases
    test_cases = [
        {
            "context": "Apple Inc. is an American multinational technology "
                       "company headquartered in Cupertino, California.",
            "question": "Where is Apple Inc. headquartered?"
        },
        {
            "context": "The M4 Pro chip features a 16-core Neural Engine "
                       "capable of 38 trillion operations per second.",
            "question": "How many cores does the M4 Pro Neural Engine have?"
        },
        {
            "context": "CoreML automatically uses the Apple Neural Engine "
                       "for machine learning tasks when available.",
            "question": "What does CoreML use for machine learning?"
        }
    ]

    print("\n" + "="*60)
    print("Running ANE Inference Tests")
    print("="*60)

    total_time = 0
    successful_tests = 0

    for idx, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {idx}:")
        print(f"   Context: \"{test['context'][:80]}...\"")
        print(f"   Question: \"{test['question']}\"")

        # Tokenize
        inputs = tokenizer(
            test['question'],
            test['context'],
            return_tensors='np',
            padding='max_length',
            truncation=True,
            max_length=384
        )

        # Prepare inputs - Model expects float64 (DOUBLE) arrays of shape [1, 384]
        word_ids = inputs['input_ids'].astype(np.float64)  # Convert to float64
        word_types = inputs['token_type_ids'].astype(np.float64)  # Convert to float64

        # Ensure shape is exactly [1, 384]
        if word_ids.shape[1] != 384:
            # This shouldn't happen with padding='max_length' but just in case
            word_ids_list = word_ids[0].tolist()
            word_types_list = word_types[0].tolist()

            word_ids_list = pad_or_truncate(word_ids_list, 384)
            word_types_list = pad_or_truncate(word_types_list, 384)

            word_ids = np.array([word_ids_list], dtype=np.float64)
            word_types = np.array([word_types_list], dtype=np.float64)

        # Create input dictionary
        input_data = {
            'wordIDs': word_ids,
            'wordTypes': word_types
        }

        try:
            # Measure inference time
            start_time = time.perf_counter()
            result = model.predict(input_data)
            end_time = time.perf_counter()

            inference_time = (end_time - start_time) * 1000
            total_time += inference_time
            successful_tests += 1

            print("\n   ✅ Inference successful!")
            print(f"   ⏱️  Time: {inference_time:.2f} ms")

            # Extract answer
            if 'startLogits' in result and 'endLogits' in result:
                start_logits = result['startLogits'].flatten()
                end_logits = result['endLogits'].flatten()

                # Get best start and end positions
                start_idx = np.argmax(start_logits)
                end_idx = np.argmax(end_logits)

                # Ensure valid span
                if start_idx <= end_idx and end_idx < 384:
                    # Convert token IDs back to tokens
                    token_ids = inputs['input_ids'][0]
                    tokens = tokenizer.convert_ids_to_tokens(token_ids)

                    # Extract answer tokens
                    answer_tokens = tokens[start_idx:end_idx+1]

                    # Convert tokens to string
                    answer = tokenizer.convert_tokens_to_string(answer_tokens)

                    print(f"   💡 Predicted Answer: \"{answer}\"")
                    print(f"   📊 Answer span: [{start_idx}, {end_idx}]")
                    print(
                        f"   📈 Confidence: "
                        f"start={start_logits[start_idx]:.2f}, "
                        f"end={end_logits[end_idx]:.2f}"
                    )
                else:
                    print(f"   ⚠️  Invalid answer span: [{start_idx}, {end_idx}]")

        except Exception as exc:  # noqa: BLE001 (module-isolation)
            print(f"\n   ❌ Inference failed: {exc}")

    # Summary
    print("\n" + "="*60)
    print("📊 Performance Summary")
    print("="*60)

    if successful_tests > 0:
        avg_time = total_time / successful_tests
        print(f"✅ Successful tests: {successful_tests}/{len(test_cases)}")
        print(f"⏱️  Average inference time: {avg_time:.2f} ms")
        print(f"🚀 Throughput: ~{1000/avg_time:.1f} predictions/second")
    else:
        print("❌ No successful tests")

    print("\n" + "="*60)
    print("💡 ANE Verification")
    print("="*60)
    print("To verify Apple Neural Engine usage:")
    print("1. Open Activity Monitor")
    print("2. Go to Window → GPU History")
    print("3. Look for activity in the ANE section")
    print("\nThe M4 Pro's 16-core Neural Engine provides:")
    print("• 38 TOPS (trillion operations per second)")
    print("• Optimized FP16 inference")
    print("• Automatic dispatch via CoreML")
    print("="*60)

    return 0 if successful_tests > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
