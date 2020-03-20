from anytree import NodeMixin, RenderTree
class MyBaseClass(object):  # Just an example of a base class
  foo = 4
class MyClass(MyBaseClass, NodeMixin):  # Add Node feature
  def __init__(self, name, length, width, parent=None, children=None):
    super(MyClass, self).__init__()
    self.name = name
    self.length = length
    self.width = width
    self.parent = parent
    if children:  # set children only if given
      self.children = children

my0 = MyClass('my0', 0, 0, children=[
  MyClass('my1', 1, 0),
  MyClass('my2', 0, 2),
])
for child in my0.children:
  print(child)

print(RenderTree(my0))