# from pathlib import Path

# from ..test_utils import load_data
# from .templates import (
#     add_test_function_metadata,
#     parse_name_function_tested,
#     t___init__,
# )


# def main():
#     PATH_TEST_DEF = Path(__file__).parent / "test_Notes.json"
#     data = load_data(path_test_def=PATH_TEST_DEF, path_test_notes=None)

#     for t_fn in [t___init__]:
#         name_f = parse_name_function_tested(t_fn.__name__)
#         test_ids: list[str] = list(data["tests"][f"tests-{name_f}"].keys())
#         for tid in test_ids:
#             add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data)


# main()
