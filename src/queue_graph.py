import matplotlib.pyplot as plt

vehicles=[10,20,30,40,50]

random=[85,105,125,160,190]

nearest=[70,85,95,115,135]

cpu=[60,75,85,95,110]

queue=[35,42,48,60,68]

plt.figure(figsize=(8,5))

plt.plot(vehicles,random,label='Random',marker='o')
plt.plot(vehicles,nearest,label='Nearest',marker='s')
plt.plot(vehicles,cpu,label='CPU',marker='^')
plt.plot(vehicles,queue,label='Queue Aware',marker='D')

plt.xlabel('Vehicles')
plt.ylabel('Queue Delay')

plt.title('Average Queue Delay')

plt.legend()

plt.grid()

plt.savefig(
'results/queue_delay.png'
)

print('Queue graph saved')
