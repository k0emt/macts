import subprocess
import time

__author__ = 'k0emt'

# use subprocess.call() to call/open all of the agents
# reference: http://docs.python.org/library/subprocess.html#module-subprocess
# more specifically: http://docs.python.org/library/subprocess.html#replacing-the-os-spawn-family

# Infrastructure/setup
# Agents: OddAgent, EvenAgent, LinearAgent
# Aggregators: EvenAndLinearAggregatorAgent, EvenAndOddAggregatorAgent
# SystemTickAgent with the number of ticks to simulate

print '\ndo you have the viewer started?'
subprocess.call('python Infrastructure.py')
time.sleep(3)

program_list = ('EvenAgent.py','LinearAgent.py','OddAgent.py',
                'EvenAndLinearAggregator.py')

for program in program_list:
    subprocess.Popen(["python", program])

time.sleep(5)
subprocess.call('python SystemTickAgent.py')
