d=set()
d.add('hello')
d.add('no')

c=set()
c.add('hello')
c.add('no')
c.add('yes')
print(c.issuperset(d))