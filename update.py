from workflow import PasswordNotFound, Workflow, web
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
            """`cached_data` can only take a bare callable (no args),
            so we need to wrap callables needing arguments in a function
            that needs none.
            """
            session_id = wf.get_password("session_id")
            return get_tree(session_id)

        nodes = wf.cached_data("workflowy_tree", wrapper, max_age=10)
        # Record our progress in the log file
        wf.logger.debug("{} Workflowy nodes cached".format(len(nodes)))

    except PasswordNotFound:  # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error("No API key saved")


if __name__ == "__main__":
    wf = Workflow()
    wf.run(main)
