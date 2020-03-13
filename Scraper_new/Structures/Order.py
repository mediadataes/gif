from operator import ge, itemgetter
from typing import Callable, Any, Union, Iterable

from multiprocessing import Manager

class Proc_safe_list():
    def __init__(self, data=[], *, _manager:Manager=None):
        self._manager = _manager or Manager()
        self.__data = self._manager.list(data)
        
    def append(self, *args): self.__data.append(*args)
    def count(self, *args): self.__data.count(*args)
    def extend(self, *args): self.__data.extend(*args)
    def index(self, *args): self.__data.index(*args)
    def insert(self, *args): self.__data.insert(*args)
    def pop(self, *args): self.__data.pop(*args)
    def remove(self, *args): self.__data.remove(*args)
    def reverse(self, *args): self.__data.reverse(*args)
    def sort(self, *args): self.__data.sort(*args)
    def clear(self): 
        while(len(self.__data)): self.__data.pop(0)


    def __deepcopy__(self): return self.__data.__deepcopy__()
    def __getitem__(self, value): return self.__data.__getitem__(value)
    def __setitem__(self, key, value): self.__data.__setitem__(key,value)
    def __delitem__(self, key): self.__data.__delitem__(key)
    def __len__(self): return self.__data.__len__()
    def __reversed__(self): return self.__data.__reversed__()
    def __contains__(self, value): return self.__data.__contains__(value)
    def __repr__(self): return self.__data.__repr__()
    def __str__(self): return self.__data.__str__()
    def __dir__(self): return self.__data.__dir__()
    def __eq__(self, value): return self.__data.__eq__(value)
    def __ne__(self, value): return self.__data.__ne__(value)
    def __sizeof__(self): return self.__data.__sizeof__()

class OrderedList(Proc_safe_list):
    def __init__(self, data:Union[dict, list]=[], *, key:Callable[[list],Any]=itemgetter(1),
                        sort_by:Callable[[Any,Any],bool]=ge, reverse:bool=False, is_dict:bool=None,
                        _manager=None):
        self.sort_by  = sort_by
        self.reverse = reverse
        self.indices = {}

        if(isinstance(data,dict) or is_dict):
            self.is_dict = True

            if(isinstance(data,dict)):
                data = list(data.items())
            
            data = OrderedList.sort_dict(data, sort_by, key, reverse)

            self.indices = OrderedList.sorted_dict_indices([value[1]for value in data]) 

            super().__init__([key[0] for key in data], _manager=_manager)

        else:
            self.is_dict = False

            super().__init__(OrderedList.sort_list(data, sort_by, reverse), _manager=_manager)

    def append(self, data:Any):
        if(self.is_dict and len(data) == 2):
            self._append_dict(*data)
            return
        elif(not self.is_dict):
            try:
                self._append_list(data)
                return
            except Exception: pass

        super().append(data)

    def extend(self, data:Any):
        if(self.is_dict and isinstance(data,dict)):
            data = list(data.items())
        if(isinstance(data,Iterable) and len(data) and len(data[0]) == 2):
            for d in data:
                self.append(d)
            return
        super().extend(data)

    def _append_dict(self, data:Any, o_index:Any) -> None:
        index = self.indices.get(o_index, None)

        if(index is None):
            self._append_index(o_index, add=1)
            index = self.indices[o_index]

        super().insert(index, data)

    def _append_list(self, data, *, list_:list=None):
        if(list_ is None): list_ = super()

        if(self.reverse): 
            sort_by = lambda e1, e2: not self.sort_by(e1,e2)
        else:
            sort_by = self.sort_by

        for num,(ind,pos) in enumerate(list_):
            if(sort_by(pos, data) and self.reverse):
                list_.insert(num, data)
                return
            elif(not self.reverse):
                list_.insert(num, data)
                return
        else:
            list_.append(data)

    def _append_index(self, index:Any, *, add:int=0, add_self:bool=False):
        pre_pos = 0 
        indices = list(self.indices.items())
        num = 0

        if(not self.reverse): 
            indices = indices[::-1]
        else:
            print(end='')

        for num,(ind,pos) in enumerate(indices):
            if(self.sort_by(ind, index)):
                pre_pos = pos
                if(self.reverse): 
                    indices.insert(num, (index,pre_pos))
                    break
            elif(not self.reverse):
                indices.insert(num, (index,pre_pos))
                break
        else:
            indices.append((pre_pos,index))
        
        if(not self.reverse): 
            indices = indices[::-1]

        if(add):
            if(not add_self): num += 1

            self.__add_indices_pos(index, add, start_from=num, 
                                    indices=indices, found=True)

        self.indices = dict(indices)

    def __add_indices_pos(self, index:Any, add:int=1, *, start_from:int=0, 
                                indices:list=None, found:bool=False):
        if(indices is None):
            indices = list(self.indices.items())

        for num,(ind,pos) in enumerate(indices[start_from:], start_from):
            if(found):
                indices[num] = (ind, pos+add)
            else:
                if(ind == index):
                    found = True
                    indices[num] = (ind, pos+add)


    @staticmethod
    def sort_list(data:list, sort_by:Callable[[Any,Any],bool]=ge, reverse:bool=False) -> list:
        # https://medium.com/@george.seif94/a-tour-of-the-top-5-sorting-algorithms-with-python-code-43ea9aa02889
        for i in range(len(data)):
            cursor = data[i]
            pos = i
            
            while pos > 0 and sort_by(data[pos - 1], cursor):
                # Swap the number down the list
                data[pos] = data[pos - 1]
                pos = pos - 1
            # Break and do the final swap
            data[pos] = cursor

        if(reverse): data.reverse()

        return data

    @staticmethod
    def sort_dict(data:dict, sort_by:Callable[[Any,Any],bool]=ge, 
                        key:Callable[[list],Any]=itemgetter(1), reverse:bool=False) -> dict:
        if(isinstance(data,dict)):
            data = list(data.items())
        
        
        items_sort_by = lambda e1, e2: sort_by(key(e1),key(e2))

        return OrderedList.sort_list(data, items_sort_by, reverse)

    @staticmethod 
    def sorted_dict_indices(data:list, *, last:bool=False) -> dict:
        result = {}

        if(last):
            data = data[::-1]

        for num,value in enumerate(data):
            if(result.get(value, None) is None):
                result[value] = num

        if(last):
            result = dict(list(result.items())[::-1])

        return result

def test(*args, **kwargs):
    print(OrderedList(*args, **kwargs))

def test2(*args, **kwargs):
    o = OrderedList(*args, **kwargs)
    o.append(6)
    print(o[:])
    o = OrderedList(*args, **kwargs)
    o.append([6])
    print(o[:])
    o = OrderedList(*args, **kwargs)
    o.append({200:0})
    print(o[:])
    o = OrderedList(*args, **kwargs)
    o.append({200:3})
    print(o[:])

if __name__ == "__main__":
    from operator import le
    print("()")
    test2()
    print("\n[]")
    test2([1,2,4,7,3,40])
    print("\n[], reverse")
    test2([1,2,4,7,3,40],reverse=True)
    print("\n[], le")
    test2([1,2,4,7,3,40],sort_by=le)
    print("\n{}")
    test2({1:1,2:2,4:8,7:5,3:3,40:3})
    print("\n{}, reverse")
    test2({1:1,2:2,4:8,7:5,3:3,40:3},reverse=True)
    print("\n{}, le")
    test2({1:1,2:2,4:8,7:5,3:3,40:3},sort_by=le)