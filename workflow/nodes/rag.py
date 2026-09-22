from infrastructure.tools.local_search import search_local


def retrieve_context(state):
    context = search_local(state["goal"], k=3)
    return {"context": context}
