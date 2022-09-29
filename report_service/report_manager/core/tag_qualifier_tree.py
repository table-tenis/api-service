class Tree:
    def __init__(self, key, name='') -> None:
        self.key = [0,0,0,0]
        self.name = name
        for i in range(len(key)):
            self.key[i] = key[i]
        self.parent = None
        self.children = []
    
    def is_root(self):
        return (self.parent == None)
    
    def is_external(self):
        return (len(self.children) == 0)
    
    def add_child(self, child):
        assert isinstance(child, Tree)
        if child not in self.children:
            child.key[3] = self.key[1]
            self.children.append(child)
            child.parent = self
    
    def add_children(self, child_list):
        for child in child_list:
            self.add_child(child)
    
class TagQualifierTreeList:
    def __init__(self, tree_list = []) -> None:
        self.tree_list = [] # List Of Trees
        for tree in tree_list:
            self.tree_list.append(tree)
        self.deep_list = {}
    
    def size(self):
        return len(self.tree_list)
    
    def empty(self):
        return  (self.size() == 0)
    
    def root(self):
        if not self.empty():
            for tree in self.tree_list:
                if tree.is_root():
                    return tree
        return None
    
    def get_tree(self, key):
        for tree in self.tree_list:
            if tree.key == key:
                return tree
        return None

    def add_tree(self, tree):
        found = False
        print("add tree = ", tree.key)
        for exist_tree in self.tree_list:
            if exist_tree.key == tree.key:
                print("not found, ", exist_tree.key, tree.key)
                found = True
                break
        if not found:
            print("append tree = ", tree.key)
            self.tree_list.append(tree)
            if self.deep_list.get(tree.key[0]) == None:
                self.deep_list[tree.key[0]] = [tree]
            else:
                self.deep_list[tree.key[0]].append(tree)
                
    def height(self, tree):
        h = 0
        if tree.is_external():
            return tree.key[0]
        for node in tree.children:
            h = max(h, self.height(node))
        return h
    
    def match_qualifier(self, subtree, tag_qualifier):
        match = False
        if tag_qualifier[subtree.key[0]] == -1:
            match = True
        elif subtree.key[1] == -1 and tag_qualifier[subtree.key[0]] == -1:
            match = True
        elif subtree.key[1] == -1 and tag_qualifier[subtree.key[0]] != -1:
            subtree.key[1] = tag_qualifier[subtree.key[0]]
            match = True    
        elif subtree.key[1] == tag_qualifier[subtree.key[0]]:
            match = True
            
        if match:
            print("match: ", subtree.key[1], tag_qualifier[subtree.key[0]])
            children = subtree.children[:]
            for child in children:
                self.match_qualifier(child, tag_qualifier)
                
        else:
            print('prune: ', subtree.key)
            self.remove_brach(subtree)
        print("height of ", subtree.key, " = ", self.height(subtree))
        return subtree
       
    def remove_brach(self, tree):
        if tree.parent:
            try:
                tree.parent.children.remove(tree)
            except ValueError as e:
                print(e, tree.key)
            if not tree.parent.is_root() and len(tree.parent.children) == 0:
                self.remove_brach(tree.parent)
        tree.children = []
        try:
            self.delete_tree(tree) 
        except ValueError as e:
            print(e, tree.key)
     
    def pruning_tree(self, tag_qualifier):
        subtree_list = []
        subtree_group_0 = self.deep_list[0][:]
        for subtree in subtree_group_0:
            subtree_list.append(self.match_qualifier(subtree, tag_qualifier))
        
        subtree_list = self.deep_list[0]
        for tree in subtree_list:
            if self.height(tree) < (len(tag_qualifier)-1):
                self.delete_tree(tree)
    
    def delete_tree(self, tree):
        self.deep_list[tree.key[0]].remove(tree)
        self.tree_list.remove(tree)

    def subtree_group(self, id):
        deep_0 = self.deep_list[0]
        for tree in deep_0:
            if tree.key[1] == id:
                return tree.key[2]
        return None
    
    def print_subtree(self, subtree):
        if not subtree:
            return 
        print(subtree.key)
        # print('\n')
        children = subtree.children
        for child in children:
            self.print_subtree(child)


def verify_query_params(query_params, tag_qualifiers):
    for i in range(len(query_params)):
        if not query_params[i]:
            query_params[i] = -1
    tree_list = TagQualifierTreeList()
    subtree_group_index = 0
    deep_0_node = []
    for tag_qualifier in tag_qualifiers:
        if tag_qualifier[0] not in deep_0_node:
            deep_0_node.append(tag_qualifier[0])
    print(deep_0_node)
    
    # Add First Deep_0 Tree To TagQualifierTreeList
    for val in deep_0_node:
        tree = tree_list.get_tree([0, val, subtree_group_index, 0])
        if not tree:
            tree = Tree([0, val, subtree_group_index, 0])
            subtree_group_index += 1
            tree_list.add_tree(tree)
    
    # Add All Child To TreeList
    for tag_qualifier in tag_qualifiers:
        for i in range(len(tag_qualifier)-1):
            if i == 0:
                prev_tree = tree_list.get_tree([i, tag_qualifier[i], tree_list.subtree_group(tag_qualifier[0]), 0])
            else:
                prev_tree = tree_list.get_tree([i, tag_qualifier[i], tree_list.subtree_group(tag_qualifier[0]), tag_qualifier[i-1]])
            if not prev_tree:
                prev_tree = Tree([i, tag_qualifier[i], tree_list.subtree_group(tag_qualifier[0]), tag_qualifier[i-1]])
            post_tree = tree_list.get_tree([i+1, tag_qualifier[i+1], tree_list.subtree_group(tag_qualifier[0]), tag_qualifier[i]])
            if not post_tree:
                post_tree = Tree([i+1, tag_qualifier[i+1], tree_list.subtree_group(tag_qualifier[0]), tag_qualifier[i]])
            prev_tree.add_child(post_tree)
            tree_list.add_tree(prev_tree)
            tree_list.add_tree(post_tree)
            
    # After Complete Contruct User Tree As TreeList.
    # Prunching TreeList With query params To Get Matched Tree For Query
    print(len(tree_list.deep_list[0]), len(tree_list.tree_list))
    for tree in tree_list.tree_list:
        print("----", tree.key, tree.name)
    for tree in tree_list.deep_list[0]:
        print_subtree(tree)
    tree_list.pruning_tree(query_params)
    return tree_list.deep_list[0]

def print_subtree(subtree):
    if not subtree:
        return 
    print(subtree.key, subtree.name)
    # print('\n')
    children = subtree.children
    for child in children:
        print_subtree(child)

def gender_query(tree):
    if tree.key[1] == -1 and tree.key[0] != -1:
        return ""
    id = ""
    if tree.key[1] != -1:
        id = tree.name + str(tree.key[1])

    sub_id = ""
    for child in tree.children:
        if sub_id == "":
            if id != "":
                sub_id += "( " + gender_query(child)
            else:
                sub_id += gender_query(child)
        else:
            sub_id += " or " + gender_query(child)
        
    if sub_id != "":
        if id == "":
            id = "(" + sub_id + ")"
        else:
            if sub_id != "( ":
                sub_id += " )"
                id  = "( " + id + " and " + sub_id + " )"   
    return id

def labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'site.enterprise_id = '
    elif tree.key[0] == 1:
        tree.name = 'camera.site_id = '
    elif tree.key[0] == 2:
        tree.name = 'camera.id = '
    for child in tree.children:
        labeling_tree(child)
        
def tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    labeling_tree(root)
    # print_subtree(root)
    return gender_query(root)

def site_labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'site.enterprise_id = '
    elif tree.key[0] == 1:
        tree.name = 'site.id = '
    for child in tree.children:
        site_labeling_tree(child)
        
def site_tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    site_labeling_tree(root)
    # print_subtree(root)
    return gender_query(root)

if __name__ == '__main__':
    query_params = [None,None,None]
    tag_qualifiers = [[1,2,5],[1,2,6], [1,3,-1], [1,4,-1]]
    # tag_qualifiers = [[1,2,1,9], [1,2,2,10], [1,2,3,11], [1,2,3,12], [1,4,7,13], [1,4,7,14], [1,4,7,15]]
    match_tree_list = verify_query_params(query_params, tag_qualifiers) 
    print(len(match_tree_list))
    for tree in match_tree_list:
        print('------------')
        print_subtree(tree)
    print(site_tree_to_query(match_tree_list))