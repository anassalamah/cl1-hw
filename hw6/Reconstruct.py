def _reconstruct(self, span):
        """
        Return an iterater over edges in a cell in the parse chart
        """
	result = set()
       	print self._pointer[span]
       	print "1st RIC", (span[0],self._pointer[span])
       	# add span1 of depth 1
       	result.add((span[0],self._pointer[span])) 
       	print "1st RIC 1", (self._pointer[span],self._chart[(span[0],self._pointer[span], False, True)])
       	# add span1/span1 of depth 2
       	result.add((self._pointer[span],self._chart[(span[0],self._pointer[span], False, True)]))
       	print "1st RIC 2", (self._chart[(span[0],self._pointer[span], False, True)],self._chart[(span[0], self._chart[(span[0],self._pointer[span], False, True)], False, True)])
       	# add span1/span2 of depth 2
       	result.add((self._chart[(span[0],self._pointer[span], False, True)],self._chart[(span[0], self._chart[(span[0],self._pointer[span], False, True)], False, True)]))
       	print "1st RC", (self._pointer[span], span[1])
       	# add span2 of depth 1
       	#result.add((self._pointer[span], span[1]))
       	
       	print self._pointer[(self._pointer[span], span[1], True, True)]
       	print "1st RC RIC" ,(self._pointer[span],self._pointer[(self._pointer[span], span[1], True, True)])
       	# add span2/span1 of depth 2
       	result.add((self._pointer[span],self._pointer[(self._pointer[span], span[1], True, True)]))
       	print " 1st RC RC", (self._pointer[(self._pointer[span], span[1], True, True)], span[1])
       	# add span2/span2 of depth 2
       	result.add((self._pointer[(self._pointer[span], span[1], True, True)], span[1]))
       	print "1st RC RC 1", (span[1]), self._pointer[(4,6,False,True)]
       	# add last span
       	result.add((span[1], self._pointer[(4,6,False,True)]))
       	
       	print "THIS IS IT", result      	
        return result