from workflow import PasswordNotFound, Workflow3
from workflowy_api.transport import Transport
from workflowy_api.tree import Tree


def get_tree(session_id):
    tree_dict, saved_views, transaction_id = Transport.get_initialization_data(
        session_id
    )
    return Tree(tree_dict, saved_views, False), Tree(tree_dict, saved_views, True),  transaction_id


def main(wf):
    def wrapper():
        session_id = wf.get_password("session_id")
        return get_tree(session_id)

    wf.cached_data("workflowy_tree", wrapper, max_age=1)
    # Record our progress in the log file
    wf.logger.debug("Workflowy nodes cached")



if __name__ == "__main__":
    wf = Workflow3()
    wf.run(main)
