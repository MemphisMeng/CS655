import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# read data from csv files which is recorded in the tests
RTT = pd.read_csv('./RTT.csv', header=None)
RTT_custom = pd.read_csv('./RTT_custom.csv', header=None)
TPUT = pd.read_csv('./TPUT.csv', header=None)
TPUT_custom = pd.read_csv('./TPUT_custom.csv', header=None)

# change the names of columns of message sizes, types and delays
RTT.rename({30: 'TYPE', 31:'msgSize', 32:'delay'}, axis=1, inplace=True)
RTT_custom.rename({30: 'TYPE', 31:'msgSize', 32:'delay'}, axis=1, inplace=True)
TPUT.rename({30: 'TYPE', 31:'msgSize', 32:'delay'}, axis=1, inplace=True)
TPUT_custom.rename({30: 'TYPE', 31:'msgSize', 32:'delay'}, axis=1, inplace=True)

# average the values among all the 30 experiments
RTT['average'] = RTT[range(30)].mean(axis=1) * 1e3
RTT_custom['average'] = RTT_custom[range(30)].mean(axis=1) * 1e3
TPUT['average'] = TPUT['msgSize'] * 8 * 1e-6 / TPUT[range(30)].mean(axis=1)
TPUT_custom['average'] = TPUT_custom['msgSize'] * 8 * 1e-6 / TPUT_custom[range(30)].mean(axis=1)


def draw_delay(df, type):
	# create a new figure window 
	plt.figure()
	plt.plot(df['msgSize'].loc[df['delay'] == 0.0], df['average'].loc[df['delay'] == 0.0], color='blue', alpha=0.5, ls =':', marker='+')
	plt.plot(df['msgSize'].loc[df['delay'] == 1000.0], df['average'].loc[df['delay'] == 1000.0], color='red', alpha=0.5, ls =':', marker='+')
	plt.plot(df['msgSize'].loc[df['delay'] == 2000.0], df['average'].loc[df['delay'] == 2000.0], color='green', alpha=0.5, ls =':', marker='+')

	# legend
	plt.legend(labels=['delay = 0 ms', 'delay = 1000 ms', 'delay = 2000 ms'])
	# title and labels.
	if type == 'rtt':
		plt.title('Relationship between Message Size and Round Trip Time')
		plt.xlabel('Message Size(bytes)')
		plt.ylabel('Latency (ms)')
		# save image
		plt.savefig('Message Size vs Round Trip Time (variable delays).png')
	else:
		plt.title('Relationship between Message Size and Throughput')
		plt.xlabel('Message Size(bytes)')
		plt.ylabel('Throughput (Mbps)')
		plt.savefig('Message Size vs Throughput (variable delays).png')


def draw_server(df1, df2, type):
	# create a new figure window 
	plt.figure()
	plt.plot(df1['msgSize'].loc[df1['delay'] == 0.0], df1['average'].loc[df1['delay'] == 0.0], color='blue', alpha=0.5, ls =':', marker='+')
	plt.plot(df2['msgSize'].loc[df2['delay'] == 0.0], df2['average'].loc[df2['delay'] == 0.0], color='red', alpha=0.5, ls =':', marker='+')
	
	# legend
	plt.legend(labels=['California server', 'Customed server'])
	# title and labels
	if type == 'rtt':
		plt.title('Relationship between Message Size and Round Trip Time')
		plt.xlabel('Message Size(bytes)')
		plt.ylabel('Latency (ms)')
		# save image
		plt.savefig('Message Size vs Round Trip Time (variable servers).png')
	else:
		plt.title('Relationship between Message Size and Throughput')
		plt.xlabel('Message Size(bytes)')
		plt.ylabel('Throughput (Mbps)')
		plt.savefig('Message Size vs Throughput (variable servers).png')


if __name__ == '__main__':
	# draw the figure describing the relation between RTTs and delay time
	draw_delay(RTT, 'rtt')
	# draw the figure describing the relation between TPUTs and delay time
	draw_delay(TPUT, 'tput')

	# draw the figure describing the relation between RTTs and server locations
	# draw_server(RTT, RTT_custom, 'rtt')
	# draw the figure describing the relation between TPUTs and server locations
	# draw_server(TPUT, TPUT_custom, 'tput')