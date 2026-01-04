"""
Cost estimator for AI API usage in ATS CV Maker.
Helps users understand approximate costs before running analyses.
"""

# Approximate token counts (conservative estimates)
AVG_JD_TOKENS = 500  # Average job description
AVG_KEYWORDS = 30    # Average keywords to rate
SYSTEM_PROMPT_TOKENS = 200
RESPONSE_TOKENS = 300

# Pricing per 1M tokens (as of 2024)
PRICING = {
    'gpt-4': {
        'input': 30.00,   # per 1M input tokens
        'output': 60.00   # per 1M output tokens
    },
    'gpt-3.5-turbo': {
        'input': 0.50,
        'output': 1.50
    },
    'gpt-4-turbo': {
        'input': 10.00,
        'output': 30.00
    },
    'claude-3-opus': {
        'input': 15.00,
        'output': 75.00
    },
    'claude-3-sonnet': {
        'input': 3.00,
        'output': 15.00
    },
    'claude-3-haiku': {
        'input': 0.25,
        'output': 1.25
    }
}


def estimate_cost(model: str = 'gpt-4', num_analyses: int = 1) -> dict:
    """
    Estimate the cost of running ATS analyses.
    
    Args:
        model: The AI model to use
        num_analyses: Number of CV analyses to run
        
    Returns:
        Dictionary with cost breakdown
    """
    # Normalize model name
    model = model.lower()
    
    # Map common variants to pricing keys
    model_mapping = {
        'gpt-4': 'gpt-4',
        'gpt-4-turbo': 'gpt-4-turbo',
        'gpt-3.5-turbo': 'gpt-3.5-turbo',
        'claude-3-opus-20240229': 'claude-3-opus',
        'claude-3-sonnet-20240229': 'claude-3-sonnet',
        'claude-3-haiku-20240307': 'claude-3-haiku',
    }
    
    pricing_key = model_mapping.get(model, 'gpt-4')
    
    if pricing_key not in PRICING:
        return {
            'error': f'Unknown model: {model}',
            'available_models': list(PRICING.keys())
        }
    
    prices = PRICING[pricing_key]
    
    # Calculate token usage per analysis
    input_tokens = AVG_JD_TOKENS + AVG_KEYWORDS * 5 + SYSTEM_PROMPT_TOKENS
    output_tokens = RESPONSE_TOKENS
    
    # Calculate costs
    input_cost_per_analysis = (input_tokens / 1_000_000) * prices['input']
    output_cost_per_analysis = (output_tokens / 1_000_000) * prices['output']
    total_cost_per_analysis = input_cost_per_analysis + output_cost_per_analysis
    
    total_cost = total_cost_per_analysis * num_analyses
    
    return {
        'model': pricing_key,
        'num_analyses': num_analyses,
        'estimated_tokens': {
            'input': input_tokens,
            'output': output_tokens,
            'total': input_tokens + output_tokens
        },
        'cost_per_analysis': {
            'input': round(input_cost_per_analysis, 6),
            'output': round(output_cost_per_analysis, 6),
            'total': round(total_cost_per_analysis, 6)
        },
        'total_cost': round(total_cost, 4),
        'currency': 'USD'
    }


def print_cost_estimate(model: str = 'gpt-4', num_analyses: int = 1):
    """
    Print a formatted cost estimate.
    
    Args:
        model: The AI model to use
        num_analyses: Number of CV analyses to run
    """
    result = estimate_cost(model, num_analyses)
    
    if 'error' in result:
        print(f"❌ {result['error']}")
        print(f"Available models: {', '.join(result['available_models'])}")
        return
    
    print("=" * 60)
    print("💰 ATS CV Maker - Cost Estimate")
    print("=" * 60)
    print(f"Model: {result['model']}")
    print(f"Number of analyses: {result['num_analyses']}")
    print()
    print("Estimated tokens per analysis:")
    print(f"  Input:  {result['estimated_tokens']['input']:,} tokens")
    print(f"  Output: {result['estimated_tokens']['output']:,} tokens")
    print(f"  Total:  {result['estimated_tokens']['total']:,} tokens")
    print()
    print("Cost per analysis:")
    print(f"  Input:  ${result['cost_per_analysis']['input']:.6f}")
    print(f"  Output: ${result['cost_per_analysis']['output']:.6f}")
    print(f"  Total:  ${result['cost_per_analysis']['total']:.6f}")
    print()
    print("=" * 60)
    print(f"💵 Total Estimated Cost: ${result['total_cost']:.4f} {result['currency']}")
    print("=" * 60)
    print()
    print("Note: This is an estimate. Actual costs may vary based on:")
    print("  - Actual length of job descriptions")
    print("  - Number of keywords extracted")
    print("  - Model pricing changes")


def compare_models(num_analyses: int = 10):
    """
    Compare costs across different models.
    
    Args:
        num_analyses: Number of analyses to estimate for
    """
    print("=" * 60)
    print(f"💰 Cost Comparison for {num_analyses} Analyses")
    print("=" * 60)
    print()
    
    models = ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4', 
              'claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus']
    
    results = []
    for model in models:
        est = estimate_cost(model, num_analyses)
        if 'error' not in est:
            results.append((model, est['total_cost']))
    
    # Sort by cost
    results.sort(key=lambda x: x[1])
    
    print(f"{'Model':<25} {'Total Cost':>15}")
    print("-" * 60)
    for model, cost in results:
        print(f"{model:<25} ${cost:>14.4f}")
    
    print()
    print(f"💡 Cheapest option: {results[0][0]} (${results[0][1]:.4f})")
    print(f"🚀 Recommended: claude-3-sonnet (good balance of cost/quality)")
    print()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'compare':
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            compare_models(num)
        else:
            model = sys.argv[1]
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            print_cost_estimate(model, num)
    else:
        print("Usage:")
        print("  python cost_estimator.py <model> [num_analyses]")
        print("  python cost_estimator.py compare [num_analyses]")
        print()
        print("Examples:")
        print("  python cost_estimator.py gpt-4 5")
        print("  python cost_estimator.py claude-3-sonnet 10")
        print("  python cost_estimator.py compare 20")
        print()
        print("Running default estimate (GPT-4, 1 analysis):")
        print()
        print_cost_estimate()
