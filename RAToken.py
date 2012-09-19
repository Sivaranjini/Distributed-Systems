import sys
import random
import itertools


class RAToken(DistProcess):

    def __init__(self, parent, initq, channel, log):
        DistProcess.__init__(self, parent, initq, channel, log)
        self._event_patterns = [EventPattern(Event.receive, 'Request', [], [(1, 'tstest')], [self._event_handler_0]), EventPattern(Event.receive, 'Token', [], [(1, 'ftoken_Assign_TS')], [self._event_handler_1])]
        self._sent_patterns = []
        self._label_events = {'cs': self._event_patterns, 'start': self._event_patterns, 'await': self._event_patterns, 'release': self._event_patterns}

    def setup(self, reqProcess, processList, processRequestCnt, initial_tokenvalue):
        self.ts = 0
        self.process_Id = self._id
        self.processRequest_TS = dict.fromkeys(processList, 0)
        self.token_Assign_TS = dict.fromkeys(processList, 0)
        self.token_present = initial_tokenvalue
        self.token_held = False
        self.processList = processList
        self.reqProcess = reqProcess
        self.requestCount = processRequestCnt
        self.requestNo = 0
        self.processList = processList
        self.processRequestCnt = processRequestCnt
        self.reqProcess = reqProcess
        self.initial_tokenvalue = initial_tokenvalue

    def cs(self, task):
        self._label_('start')
        self.ts+=1
        if (not self.token_present):
            self.output(REQUESTING + ('Process Id: ') + (str(self.process_Id)) + (' Request No: ') + (str(self.requestNo)) + (' REQUESTING CS') + (EXIT))
            self.processRequest_TS[self.process_Id] = self.ts
            self.send(('Request', self.ts), self.reqProcess)
        self._label_('await')
        while (not (self.token_present == True)):
            self._process_event(self._event_patterns, True, None)
        self.token_Assign_TS[self.process_Id] = self.ts
        self.token_held = True
        self._label_('cs')
        task()
        self._label_('release')
        self.output(LEAVING + ('Process Id: ') + (str(self.process_Id)) + (' Request No: ') + (str(self.requestNo)) + (' LEAVING CS') + (EXIT))
        self.release()

    def main(self):

        def anounce():
            self.output(ENTERING + ('Process Id: ') + (str(self.process_Id)) + (' Request No: ') + (str(self.requestNo)) + (' ENTERING CS') + (EXIT))
        for i in range(1, self.requestCount + (1)):
            self.requestNo = i
            self.cs(anounce)
        self._label_('await')
        while (not (self.token_present == False)):
            self._process_event(self._event_patterns, True, None)

    def _event_handler_0(self, tstest, _timestamp, _source):
        self.processRequest_TS[_source] = max(self.processRequest_TS[_source], tstest)
        if ((self.token_present == True) and (self.token_held == False)):
            self.release()

    def _event_handler_1(self, ftoken_Assign_TS, _timestamp, _source):
        self.token_present = True
        self.token_Assign_TS = ftoken_Assign_TS

    def release(self):
        self.token_Assign_TS[self.process_Id] = int(self.ts)
        self.token_held = False
        index = self.processList.index(self.process_Id)
        for i in itertools.chain(range(index + (1), 
        len(self.processList)), 
        range(0, index - (1))):
            if (self.processRequest_TS[self.processList[i]] > self.token_Assign_TS[self.processList[i]]):
                self.token_present = False
                self.send(('Token', self.token_Assign_TS), self.processList[i])
                break