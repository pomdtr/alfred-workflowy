from workflow import PasswordNotFound, Workflow3
from workflowy_api.transport import Transport
from workflowy_api.tree import Tree


def get_tree(session_id, with_completed=True):
    tree_dict, saved_views, transaction_id = Transport.get_initialization_data(
        session_id
    )
    return Tree(tree_dict, saved_views, with_completed), transaction_id


def main(wf):
    try:

        def wrapper():
            session_id = wf.get_password("session_id")
            return get_tree(session_id)

        nodes = wf.cached_data("workflowy_tree", wrapper, session=True)
        # Record our progress in the log file
        wf.logger.debug("{} Workflowy nodes cached".format(len(nodes)))

    except PasswordNotFound:  # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error("No API key saved")


if __name__ == "__main__":
    wf = Workflow3()
    wf.run(main)
