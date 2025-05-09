from heapq import heappush, heappop

class PriorityQueue(object):
	''' Cost sorted (min-to-max) queue. Equal cost items revert to FIFO order.'''

	def __init__(self):
		self.q = []
		self.i = 0 # default order counter

	def push(self, item, cost):
		'''Add an item and its cost to the queue. '''
		heappush(self.q, (cost, self.i, item))
		self.i += 1

	def pop(self):
		'''Remove the item of lowest cost, or FIFO order if cost equal.
		Returns the item (whatever it is) and the cost as a tuple. '''
		cost, i, item = heappop(self.q)
		return item, cost

	def __len__(self):
		return len(self.q)

	def __str__(self):
		'''Print a sorted view of the queue contents. '''
		return 'pq: ' + str(sorted(self.q))

	def __contains__(self, item):
		return any(item == values[2] for values in self.q)

	def __iter__(self):
		'''Support iteration. This enables support of the "in" operator. '''
		return iter(values[2] for values in self.q)

	def peek(self, item):
		'''Return a tuple of (item, cost) if it exists, without removing. '''
		for values in self.q:
			if values[2] == item:
				return (item, values[0])

	def remove(self, item):
		'''Remove the first item that matches.'''
		for i, values in enumerate(self.q):
			if values[2] == item:
				del self.q[i]
				return


class Path(object):
	''' Convenient container and converter for route-path information'''
	def __init__(self, graph, route, target_idx, open, closed, steps):
		# keep any data if we are asked
		self.route = route
		self.open = open
		self.closed = closed
		self.target_idx = target_idx
		self.steps = steps

		# Convert dictionary back in to a list of nodes for a path
		if target_idx in route:
			path = []
			curr_idx = target_idx
			while curr_idx != route[curr_idx]:
				path.append(curr_idx)
				curr_idx = route[curr_idx]
			self.result = 'Success! '

			self.result += 'Still going...' if target_idx in open else 'Done!'
			path.append(curr_idx)
			path.reverse()
			self.path = path
			self.path_cost = str(graph.path_cost(path))
			self.source_idx = curr_idx
		else:
			self.result = 'Failed.'
			self.path = []
			self.path_cost = '---'

	
	def report(self, verbose=3):
		tmp = "%s Steps: %d Cost: %s\n" % (self.result, self.steps, self.path_cost)
		if verbose > 0:
			tmp += "Path (%d)=%s\n"  % (len(self.path), self.path)
		if verbose > 1:
			tmp += "Open (%d)=%s\n"   % (len(self.open), self.open)
			tmp += "Closed (%d)=%s\n"   % (len(self.closed), self.closed)
		if verbose > 2:
			tmp += "Route (%d)=%s\n"   % (len(self.route), self.route)
		return tmp

def SearchDijkstra(graph, source_idx, target_idx, limit=0):
    ''' Dijkstra Search. Expand the minimum path cost-so-far '''
    closed = set() # set - of visited nodes
    route = {} # dict of {to:from} items to find our way home
    open = PriorityQueue() # priority queue of the current leaf edges
    steps = 0 # if limit

    # add starting node, with cost-so-far (G)
    open.push( source_idx, 0.0 )
    route[source_idx] = source_idx # to:from
    # search loop
    while len(open):
        steps += 1
        leaf, cost = open.pop() # get the lowest cost-so-far node to investigate
        closed.add(leaf)
        if leaf == target_idx:
            break
        else:
            idxs = graph.get_neighbours(leaf)
            for dest in idxs:
                if dest not in closed: # visited
                    cost_f = cost + graph.get_edge(leaf,dest).cost # cost_g
                    if dest in open: # old path to same node?
                        if open.peek(dest)[1] <= cost_f: # if better, keep it
                            continue
                        else: # remove the old, and the new one be added
                            open.remove(dest)
                    route[dest] = leaf # to:from
                    open.push(dest, cost_f )
        # stop early?
        if limit > 0 and steps >= limit:
            break
    # return the partial/complete path details
    return Path(graph, route, target_idx, open, closed, steps)


#==============================================================================

if __name__ == '__main__':
	import graph
	# build a sample graph
	adj_list = ((0,),(1,2,3),(2,1,5),(3,1,4),(4,3,5,6),(5,2,4,6),(6,4,5))

	g = graph.SparseGraph.FromAdjacencyList(adj_list, False)
	print(g.summary())
	print(g.get_adj_list_str())

	# test the priority queue...
	pq = PriorityQueue()
	pq.push('A',2.0)
	pq.push('B',1.0)
	pq.push('C',3.0)
	print(pq.pop()) # should give (1.0, 1, 'B')

	# cost based searches
	g = graph.SparseGraph()
	g.add_node(graph.Node())
	g.add_node(graph.Node())
	g.add_node(graph.Node())
	g.add_node(graph.Node())
	g.add_node(graph.Node())
	g.add_node(graph.Node())
	g.add_node(graph.Node())
	g.add_edge(graph.Edge(1,5,2.9))
	g.add_edge(graph.Edge(1,6,1.0))
	g.add_edge(graph.Edge(2,3,3.1))
	g.add_edge(graph.Edge(3,5,0.8))
	g.add_edge(graph.Edge(4,3,3.7))
	g.add_edge(graph.Edge(5,2,1.9))
	g.add_edge(graph.Edge(5,6,3.0))
	g.add_edge(graph.Edge(6,4,1.1))
	print(g.summary())
	print(g.get_adj_list_str())
 
	# A* Search
	if False:
		g.cost_h = SimpleTestHeuristic
		print('from 1 to 3 A*:')
		print(SearchAStar(g, 1, 3))