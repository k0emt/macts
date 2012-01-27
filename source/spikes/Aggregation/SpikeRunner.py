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

do_initiate_infrastructure = True
this_is_agent_node = False
this_is_aggregator_node = False
this_is_viewer_node = False
this_is_system_tick_agent = False

def launch_programs(agent_list):
    for program in agent_list:
        subprocess.Popen(["python", program])

if do_initiate_infrastructure:
    subprocess.call('python Infrastructure.py')
    # subprocess.Popen(['cmd','python','Infrastructure.py'], shell=True)

if this_is_agent_node:
    agent_list = ('EvenAgent.py','LinearAgent.py','OddAgent.py')
    launch_programs(agent_list)

if this_is_aggregator_node:
    aggregator_list = ('EvenAndLinearAggregator.py', 'EvenAndOddAggregatorAgent.py')
    launch_programs(aggregator_list)

if this_is_viewer_node:
    subprocess.call('python Viewer.py') # this program blocks!

if this_is_system_tick_agent:
    time.sleep(5)
    subprocess.call('python SystemTickAgent.py')
    # subprocess.Popen(['cmd','python','SystemTickAgent.py'], shell=True)

