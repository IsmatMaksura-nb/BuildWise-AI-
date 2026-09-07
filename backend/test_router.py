

from backend.agents.router_agent import router_agent


def test_router():
    print("\n==============================")
    print("BuildWise-AI Router Test")
    print("==============================\n")

    test_cases = [
        ("general", "What is the purpose of a foundation?"),
        ("doc", "What is the size of the lift in this document?"),
        ("visual", "Inspect this construction image for cracks."),
        ("cost", "Estimate the construction cost of a 1500 sqft house."),
        ("market", "What is the current price of BSRM rod in Bangladesh?")
    ]

    for feature, query in test_cases:

        result = router_agent.route(
            feature=feature,
            user_input=query
        )

        print(f"Feature : {feature}")
        print(f"Query   : {query}")
        print(f"Agent   : {result['agent']}")
        print(f"Reason  : {result['reason']}")
        print("-" * 50)


if __name__ == "__main__":
    test_router()