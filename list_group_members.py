import vk_api
import json
import collections
import time

indent = "	"


def SortByInc (elem):
	return elem


deq = collections.deque (maxlen = 4)
def waitingBeforeMakeRequest (callFunction):
	def wrapperAroundCallFunction ():
		deq.appendleft (time.time())
		if len (deq) == 4:
			print (indent, "waiting...")
			time.sleep (max (1 + deq[3] - deq[0], 0))
		callFunction ()
	return wrapperAroundCallFunction


def main ():

	"""
	Load it yourself
	"""

	login, passwd = "", ""
	
	vk_session = vk_api.VkApi (login, passwd)

	try:
		vk_session.authorization ()
	except vk_api.AuthorizationError as error_msg:
		print(error_msg)
		return

	vk = vk_session.get_api ()

	group_numbers =	vk.users.get (fields='counters')[0]['counters']['groups']
	group_step = 1000
	
	counter = 0
	maxCounter = 324

	constOffset = counter

	vk.groups.getById = waitingBeforeMakeRequest (vk.groups.getById)

	for i in range (0, int (group_numbers / group_step) + 1):
		responce = vk.groups.get (count = group_step, 
				offset = group_step * i + constOffset)

		for groupId in responce ['items']:
			groupInfo = vk.groups.getById (group_id = groupId, 
					fields = 'members_count')

			if counter > maxCounter:
				break
			try:
				groupInfo [0]['members_count']
			except KeyError:
				print ("group was deleted or banned")
				continue

			membersStep = 1000
			membersCount = groupInfo [0]['members_count'] 

			print ("members : " + 
					str(membersCount) + 
					" in " + 
					groupInfo [0]['name'])

			if membersCount == 0:
				print ("<<< WARNING. VK MAY BE WAS BANNED YOU >>>")

			stepNumbers = int (membersCount / membersStep + 0.5) + 1

			jsonData = {}
			jsonData ['name'] = groupInfo [0]['name']
			jsonData ['id'] = groupId
			jsonData ['count'] = membersCount
			jsonData ['usersId'] = []
			
			maxNum = int (stepNumbers/25.0 + 0.5) + 1

			for num in range (0, maxNum):
				print (indent, "num =", num, 
					"end", maxNum)

				statmentNumber = stepNumbers
				if stepNumbers > 25:
					statmentNumber = 25
					stepNumbers -= 25

				with vk_api.VkRequestsPool(vk_session) as pool:
					responce = pool.method_one_param ('groups.getMembers',
							{'group_id' : groupId,
							'sort' : "id_asc",
							'count' : membersStep},
							'offset',
							[x for x in range
							(num * membersStep * 25,
							num * membersStep * 25 +
							statmentNumber * membersStep,
							membersStep)])

				print (indent, range (num * membersStep * 25,
							num * membersStep * 25 +
							statmentNumber * membersStep,
							membersStep))	
		
				if len (responce) == 0:
					print ("<<< CRITICAL ERROR. VK WAS BANNED YOU >>>")
					return


				for data in responce.items ():
					jsonData ['usersId'].extend (data [1]['items'])

			jsonData ['usersId'].sort (key = SortByInc)

			filename = "./db/" + str (counter) + ".json"
			
			print (filename)

			file = open (filename, "w")
			json.dump (jsonData, 
				file, 
				sort_keys = True, 
				indent = 4, 
				ensure_ascii = False)

			file.close ()
			
			del jsonData
			counter += 1

if __name__ == '__main__':
	main ()
	
