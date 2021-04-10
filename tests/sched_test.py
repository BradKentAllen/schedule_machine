

from schedule_machine.chrono import Chronograph, Timers, get_time_stamp, job_function_tester
from time import sleep

global poll_count
poll_count = 0

def poll_test():
	global poll_count
	print('-', end='')

	poll_count +=1


def poll_test2():
	#print('-', end='')
	print('+', end='')

	#sleep(.05)


def second_function():
	print('\n')
	print(get_time_stamp('US/Pacific'))
	

def five_second_function():
	global poll_count
	print(f'\n--{poll_count}--')
	poll_count = 0

def fifteen_second_function():
	print('start 15 second function')
	sleep(4)
	print('end 15 second function')

def minute_function():
	print('minute function runs')

def test_function():
	print('this is the test function')

print('test run')

#### Create Timers
maker = Timers()

maker.create_timer('every poll', poll_test)
maker.create_timer('every poll', poll_test2)
maker.create_timer('every second', second_function)
maker.create_timer('on the 5 second', five_second_function)
maker.create_timer('on the 15 second', fifteen_second_function)
#maker.create_timer('every minute', minute_function)

#maker.create_timer('schedule', test_function, '17:32')

#### helper method to check function times
#job_function_tester(maker.timer_jobs)
#exit()

#### Run Chronograph
#Chronograph(maker.timer_jobs, 'US/Pacific')
chrono = Chronograph(maker.timer_jobs, 'US/Pacific', wait_to_run=True)

# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern'
chrono.run_timers(debug=True)







