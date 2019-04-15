class Node:

	def __init__(self, value):

		self.value = value

		self.next = None



class LinkedList:

	def __init__(self):

		self.head = None

		self.tail = None



	def add(self, value):

		n = Node(value)

		if(self.head != None):

			self.tail.next = n

			self.tail = n

		else:

			self.head = n

			self.tail = n



	def remove(self, value):

		n = self.head

		f = Node(0)

		f.next = n

		while(n != None):

			if(n.value == value):

				if(n == self.head):

					self.head = n.next

				else:

					f.next = n.next



				return True



			f = f.next

			n = n.next



		return False



	def get_list(self):

		lst = []

		n = self.head

		while(n != None):

			lst += [n.value]

			n = n.next



		return lst