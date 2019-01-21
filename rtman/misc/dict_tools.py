def merge_dicts(*dicts):
    """
    merge dictionaries recursively.
    only call recursively iff both are dicts. Otherwise, the later value will be used.

    E.g.:

    [
        {
            "A": {
                "a1": 1,
                "a2": 2
            },
            "B": {
                "b1": 1
            },
            "C": 1
        },
        {
            "A": {
                "a3": 3
            },
            "B": {
                "b1": 2
            }
        }
    ]

    shall become:

    {
        "A": {
            "a1": 1,
            "a2": 2,
            "a3": 3
        },
        "B": {
            "b1": 2
        },
        "C": 1
    },

    :param list[dicts]: dictionaries to merge.
    :return:
    """
    result = {}
    for d in dicts:
        for k, v in d.iteritems():
            if isinstance(v, dict) and \
                    k in result and \
                    isinstance(result[k], dict):
                result[k] = merge_dicts(result[k], v)
            else:
                result[k] = v
    return result