class MyClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

student = MyClass("Saujanya", 18)

print(student.name)
print(student.age)
print(isinstance(student, MyClass))