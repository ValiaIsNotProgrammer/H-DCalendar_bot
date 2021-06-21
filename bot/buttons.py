from copy import deepcopy

class Buttons:
    def __init__(self):
        self.buttons = {
                        "profile_key":
                            {"Profile":
                                 [
                                    {"My dates": "Add first date!"},
                                     {"Notifications":
                                          ['Notification time', 'Early notifications',],
                                      },
                                 ]
                            },
                        "settings_date_key":
                            {"Date settings":
                                 ['Set the current date', 'Change the date'],
                             },
                        "language_key":
                            {'Language':
                                 ['Русский', 'English'],
                             },
                        "search_key":
                            {"Search":
                                 ['Search by current date', 'Search by the specified date'],
                             },
                        "end_key": ["Back to menu", "Stop"]
                    }

    def _get_parent_keys(self, child):

        parents_keys = []

        def get_key(dictonary_recursive, child):
            def recursive_get(dct, k):
                if child in dct.values():
                    return k  # убрать при возможности - путает и не понятно зачем это возращает
                else:
                    parents_keys.append(k)
                    return get_key(dct[k], child)

            for key in dictonary_recursive:
                if type(dictonary_recursive) == list:
                    Id = [Id for Id, x in enumerate(dictonary_recursive) if child in str(x)][0]
                    parents_keys.append(Id)
                    return get_key(dictonary_recursive[Id], child)

                if (child in list(dictonary_recursive.values())[0]) or (child in list(dictonary_recursive.keys())[0]):
                    parents_keys.append(key)
                    # добавляет лишние ячейки, которые помогают избежать IndexError при проверки в makeKeyboard
                    return parents_keys

                if child in str(dictonary_recursive.values()):
                    return recursive_get(dictonary_recursive, key)

        for need_key in self.buttons:
            if child in str(self.buttons[need_key]):
                parents_keys.append(need_key)
                return get_key(self.buttons[need_key], child)

    def get_value(self, button: str) -> dict:
        def recursion_get_value(dct: dict, keys_list: list) -> dict:
            for k in keys_list:
                new_dict = dct[k]
                if k == keys_list[-1]:
                    del keys_list
                    return new_dict
                del keys_list[0]
                return recursion_get_value(dct=new_dict, keys_list=keys_list)

        dictionary_buttons = self.buttons
        origin_keys_list = self._get_parent_keys(button)
        # Делается глубокая копия листа, ибо он во время итераций будет удалятся
        copy_keys_list = deepcopy(origin_keys_list)
        return recursion_get_value(dictionary_buttons, copy_keys_list)

    def set_active(self, button):
        pass