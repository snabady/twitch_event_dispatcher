import turtle
import random

t = turtle.Turtle()
t.hideturtle()
t.screen.bgcolor("black")
t.speed(0)

for _ in range(100):
    t.penup()
    t.goto(random.randint(-300,300), random.randint(-200,200))
    t.pendown()
    t.pencolor(random.random(), random.random(), random.random())
    #t.addshape("/home/sna/earlt.gif")
    t.shape("/home/sna/earlt.gif")
    t.stamp()
    t.done()
    for _ in range(36):
        t.forward(30)
        t.right(170)

turtle.done()