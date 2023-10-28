# HW4
# REMINDER: The work in this assignment must be your own original work and must be completed alone.

class Node:
    def __init__(self, content):
        self.value = content
        self.next = None
        self.previous = None

    def __str__(self):
        return ('CONTENT:{}\n'.format(self.value))

    __repr__=__str__


class ContentItem:
    '''
        >>> content1 = ContentItem(1000, 10, "Content-Type: 0", "0xA")
        >>> content2 = ContentItem(1004, 50, "Content-Type: 1", "110010")
        >>> content3 = ContentItem(1005, 18, "Content-Type: 2", "<html><p>'CMPSC132'</p></html>")
        >>> content4 = ContentItem(1005, 18, "another header", "111110")
        >>> hash(content1)
        0
        >>> hash(content2)
        1
        >>> hash(content3)
        2
        >>> hash(content4)
        1
    '''
    def __init__(self, cid, size, header, content):
        self.cid = cid
        self.size = size
        self.header = header
        self.content = content

    def __str__(self):
        return f'CONTENT ID: {self.cid} SIZE: {self.size} HEADER: {self.header} CONTENT: {self.content}'

    __repr__=__str__

    def __eq__(self, other):
        if isinstance(other, ContentItem):
            return self.cid == other.cid and self.size == other.size and self.header == other.header and self.content == other.content
        return False

    #takes in no parameters 
    #uses ord() method to produce an integer from the sum of the ASCII of the header and then modulo 3 is used on the sum
    #returns an integer between 0 and 2 inclusive 
    def __hash__(self):
        header=self.header
        sm=0
        for char in header:
            sm+=ord(char)
        return sm % 3

class CacheList:
    ''' 
        # An extended version available on Canvas. Make sure you pass this doctest first before running the extended version

        >>> content1 = ContentItem(1000, 10, "Content-Type: 0", "0xA")
        >>> content2 = ContentItem(1004, 50, "Content-Type: 1", "110010")
        >>> content3 = ContentItem(1005, 180, "Content-Type: 2", "<html><p>'CMPSC132'</p></html>")
        >>> content4 = ContentItem(1006, 18, "another header", "111110")
        >>> content5 = ContentItem(1008, 2, "items", "11x1110")
        >>> lst=CacheList(200)
        >>> lst
        REMAINING SPACE:200
        ITEMS:0
        LIST:
        <BLANKLINE>
        >>> lst.put(content1, 'mru')
        'INSERTED: CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA'
        >>> lst.put(content2, 'lru')
        'INSERTED: CONTENT ID: 1004 SIZE: 50 HEADER: Content-Type: 1 CONTENT: 110010'
        >>> lst.put(content4, 'mru')
        'INSERTED: CONTENT ID: 1006 SIZE: 18 HEADER: another header CONTENT: 111110'
        >>> lst.put(content5, 'mru')
        'INSERTED: CONTENT ID: 1008 SIZE: 2 HEADER: items CONTENT: 11x1110'
        >>> lst.put(content3, 'lru')
        "INSERTED: CONTENT ID: 1005 SIZE: 180 HEADER: Content-Type: 2 CONTENT: <html><p>'CMPSC132'</p></html>"
        >>> lst.put(content1, 'mru')
        'INSERTED: CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA'
        >>> 1006 in lst
        True
        >>> contentExtra = ContentItem(1034, 2, "items", "other content")
        >>> lst.update(1008, contentExtra)
        'UPDATED: CONTENT ID: 1034 SIZE: 2 HEADER: items CONTENT: other content'
        >>> lst
        REMAINING SPACE:170
        ITEMS:3
        LIST:
        [CONTENT ID: 1034 SIZE: 2 HEADER: items CONTENT: other content]
        [CONTENT ID: 1006 SIZE: 18 HEADER: another header CONTENT: 111110]
        [CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA]
        <BLANKLINE>
        >>> lst.tail.value
        CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA
        >>> lst.tail.previous.value
        CONTENT ID: 1006 SIZE: 18 HEADER: another header CONTENT: 111110
        >>> lst.tail.previous.previous.value
        CONTENT ID: 1034 SIZE: 2 HEADER: items CONTENT: other content
        >>> lst.tail.previous.previous is lst.head
        True
        >>> lst.tail.previous.previous.previous is None
        True
        >>> lst.clear()
        'Cleared cache!'
        >>> lst
        REMAINING SPACE:200
        ITEMS:0
        LIST:
        <BLANKLINE>
    '''
    def __init__(self, size):
        self.head = None
        self.tail = None
        self.maxSize = size
        self.remainingSpace = size
        self.numItems = 0

    def __str__(self):
        listString = ""
        current = self.head
        while current is not None:
            listString += "[" + str(current.value) + "]\n"
            current = current.next
        return 'REMAINING SPACE:{}\nITEMS:{}\nLIST:\n{}'.format(self.remainingSpace, self.numItems, listString)  

    __repr__=__str__

    def __len__(self):
        return self.numItems

    #takes in a ContentItem and a string that is either 'mru' and 'lru'
    #if there is enough space in the list/does not execeed max size, it adds a new node to the front of the list and gets rid of items to create space to insert a new node if there is not enough space using eviction policy
    #returns 'Insertion not allowed' if content size is too big; returns'Content {content.cid} aleardy in cache, insertion not allowed' if already in the list; returns 'INSERTED: {content}' if insertions was successful
    def put(self, content, evictionPolicy):
        newNode=Node(content)
        if content.size > self.maxSize:
            return f'Insertion not allowed'
        elif content.cid in self:
            return f'Content {content.cid} aleardy in cache, insertion not allowed'
        else:
            while self.remainingSpace < content.size:
                if evictionPolicy == 'lru':
                    self.lruEvict()
                elif evictionPolicy == 'mru':
                    self.mruEvict()
        if len(self)==0:
            self.head=newNode
            self.tail=newNode
        else:
            newNode.next=self.head
            self.head.previous=newNode
            self.head=newNode
        self.numItems+=1
        self.remainingSpace-=content.size
        return f'INSERTED: {content}'

    #takes in a id to search for in Cachelist
    #checks if the id is in the list and if it is, it is moved to the front of the list 
    #returns True if found and False otherwise
    def __contains__(self, cid):
        head=self.head
        if len(self)==0:
            return False
        elif self.head.value.cid==cid:
            return True 
        elif self.tail.value.cid==cid:
            self.tail.next=self.head
            self.head.previous=self.tail
            self.head=self.tail
            self.tail=self.tail.previous
            self.tail.next=None
            self.head.previous=None
            return True
        else:
            while head:
                if head.value.cid==cid:
                    head.previous.next=head.next
                    head.next.previous=head.previous
                    temp=self.head
                    self.head=head
                    self.head.next=head
                    temp.previous=self.head
                    return True
                else:
                    head=head.next
            return False

    #takes in a id to search in the CacheList and a ContentItem
    #updates existing CacheList item to a new ContentItem if found in list; if found it is moved to front of the list which is executed in contains function
    #returns 'UPDATED {ContentItem}' if found and if not, 'Cache miss!'
    def update(self, cid, content):
        if cid in self and content.size < self.remainingSpace:
            self.remainingSpace+=self.head.value.size
            self.remainingSpace-=content.size
            self.head.value=content
            return f'UPDATED: {content}'
        else:
            return 'Cache miss!'

    #takes in no parameters   
    #removes the head of the list and makes the head point to a new head or None; increases remaining space and decrease number of items
    #returns nothing 
    def mruEvict(self):
        if self.head is None:
            self.tail=None
        elif self.head==self.tail:
            self.remainingSpace+=self.head.value.size
            self.numItems-=1
            self.head=None
            self.tail=None
        else:
            self.remainingSpace+=self.head.value.size
            self.numItems-=1
            self.head=self.head.next
            self.head.previous.next=None
            self.head.previous=None 
    
    #takes in no parameteres
    #removes the tail from the list and makes the tail point to a new tail or None; increases remaining spaces and decreses number of items
    #returns nothing
    def lruEvict(self):
        if len(self)==0:
            return None
        elif self.tail == self.head:
            self.numItems-=1
            self.remainingSpace+=self.tail.value.size
            self.tail=None
            self.head=None
        else:
            self.numItems-=1
            self.remainingSpace+=self.tail.value.size
            self.tail=self.tail.previous
            self.tail.next.previous=None
            self.tail.next=None

    #takes in no parameters
    #removes all items in the list by 'unlinking' the pointers and resests number of items to 0 and remaining spaces to the max size of the list 
    #returns 'Cleared cache!'
    def clear(self):
        node=self.head
        while node and node.next:
            node=node.next
            node.next=None
            node.previous=None
        self.head=None
        self.tail=None 
        self.remainingSpace=self.maxSize
        self.numItems=0
        return f'Cleared cache!'

class Cache:
    """
        # An extended version available on Canvas. Make sure you pass this doctest first before running the extended version

        >>> cache = Cache()
        >>> content1 = ContentItem(1000, 10, "Content-Type: 0", "0xA")
        >>> content2 = ContentItem(1003, 13, "Content-Type: 0", "0xD")
        >>> content3 = ContentItem(1008, 242, "Content-Type: 0", "0xF2")

        >>> content4 = ContentItem(1004, 50, "Content-Type: 1", "110010")
        >>> content5 = ContentItem(1001, 51, "Content-Type: 1", "110011")
        >>> content6 = ContentItem(1007, 155, "Content-Type: 1", "10011011")

        >>> content7 = ContentItem(1005, 18, "Content-Type: 2", "<html><p>'CMPSC132'</p></html>")
        >>> content8 = ContentItem(1002, 14, "Content-Type: 2", "<html><h2>'PSU'</h2></html>")
        >>> content9 = ContentItem(1006, 170, "Content-Type: 2", "<html><button>'Click Me'</button></html>")

        >>> cache.insert(content1, 'lru')
        'INSERTED: CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA'
        >>> cache.insert(content2, 'lru')
        'INSERTED: CONTENT ID: 1003 SIZE: 13 HEADER: Content-Type: 0 CONTENT: 0xD'
        >>> cache.insert(content3, 'lru')
        'Insertion not allowed'

        >>> cache.insert(content4, 'lru')
        'INSERTED: CONTENT ID: 1004 SIZE: 50 HEADER: Content-Type: 1 CONTENT: 110010'
        >>> cache.insert(content5, 'lru')
        'INSERTED: CONTENT ID: 1001 SIZE: 51 HEADER: Content-Type: 1 CONTENT: 110011'
        >>> cache.insert(content6, 'lru')
        'INSERTED: CONTENT ID: 1007 SIZE: 155 HEADER: Content-Type: 1 CONTENT: 10011011'

        >>> cache.insert(content7, 'lru')
        "INSERTED: CONTENT ID: 1005 SIZE: 18 HEADER: Content-Type: 2 CONTENT: <html><p>'CMPSC132'</p></html>"
        >>> cache.insert(content8, 'lru')
        "INSERTED: CONTENT ID: 1002 SIZE: 14 HEADER: Content-Type: 2 CONTENT: <html><h2>'PSU'</h2></html>"
        >>> cache.insert(content9, 'lru')
        "INSERTED: CONTENT ID: 1006 SIZE: 170 HEADER: Content-Type: 2 CONTENT: <html><button>'Click Me'</button></html>"
        >>> cache
        L1 CACHE:
        REMAINING SPACE:177
        ITEMS:2
        LIST:
        [CONTENT ID: 1003 SIZE: 13 HEADER: Content-Type: 0 CONTENT: 0xD]
        [CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA]
        <BLANKLINE>
        L2 CACHE:
        REMAINING SPACE:45
        ITEMS:1
        LIST:
        [CONTENT ID: 1007 SIZE: 155 HEADER: Content-Type: 1 CONTENT: 10011011]
        <BLANKLINE>
        L3 CACHE:
        REMAINING SPACE:16
        ITEMS:2
        LIST:
        [CONTENT ID: 1006 SIZE: 170 HEADER: Content-Type: 2 CONTENT: <html><button>'Click Me'</button></html>]
        [CONTENT ID: 1002 SIZE: 14 HEADER: Content-Type: 2 CONTENT: <html><h2>'PSU'</h2></html>]
        <BLANKLINE>
        <BLANKLINE>
        >>> cache[content9].next.value
        CONTENT ID: 1002 SIZE: 14 HEADER: Content-Type: 2 CONTENT: <html><h2>'PSU'</h2></html>
    """

    def __init__(self):
        self.hierarchy = [CacheList(200), CacheList(200), CacheList(200)]
        self.size = 3
    
    def __str__(self):
        return ('L1 CACHE:\n{}\nL2 CACHE:\n{}\nL3 CACHE:\n{}\n'.format(self.hierarchy[0], self.hierarchy[1], self.hierarchy[2]))
    
    __repr__=__str__


    def clear(self):
        for item in self.hierarchy:
            item.clear()
        return 'Cache cleared!'

    #takes in a ContentItem and a string which is either 'lru' or 'mru'
    #places the ContentItem in the proper CacheList
    #returns out put from the put method of the Cachelist 
    def insert(self, content, evictionPolicy):
        loc=content.__hash__()
        lst_loc=self.hierarchy[loc].put(content,evictionPolicy)
        return lst_loc

    #takes in a ContentItem
    #uses CacheList contain method to retrieve a reference to a Node 
    #returns the object contains value and "Cache miss!" if not found 
    def __getitem__(self, content):
        loc=content.__hash__()
        lst_loc=self.hierarchy[loc].__contains__(content.cid)
        if lst_loc != False:
            return lst_loc
        else:
            return f'Cache miss!'

    #takes in a ContentItem
    #uses Cachelist update function to update the content 
    #returns updated ContentItem or 'Cache miss!' if not found 
    def updateContent(self, content):
        loc=content.__hash__()
        lst_loc=self.hierarchy[loc].update(content.cid,content)
        if lst_loc is not None:
            return content
        else:
            return f'Cache miss!'