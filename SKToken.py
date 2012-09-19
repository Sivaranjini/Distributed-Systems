import sys
import random
import itertools


class SKToken(DistProcess):

    def __init__(self, parent, initq, channel, log):
        DistProcess.__init__(self, parent, initq, channel, log)
        self._event_patterns = [EventPattern(Event.receive, 'Request', [], [(1, 'fprocess_Id'), (2, 'fReqNo')], [self._event_handler_0]), EventPattern(Event.receive, 'Privilege', [], [(1, 'fQ'), (2, 'fLN')], [self._event_handler_1])]
        self._sent_patterns = []
        self._label_events = {'cs': self._event_patterns, 'start': self._event_patterns, 'await': self._event_patterns, 'release': self._event_patterns}

    def setup(self, reqProcess, processList, processRequestCnt, initial_tokenvalue):
        self.process_Id = self._id
        self.HavePrivilege = initial_tokenvalue
        self.Requesting = False
        self.Q = []
        self.RN = dict.fromkeys(processList, (-1))
        self.LN = dict.fromkeys(processList, (-1))
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
        self.Requesting = True
        if (not self.HavePrivilege):
            self.RN[self.process_Id]+=1
            self.output(REQUESTING + ('Process Id: ') + (str(self.process_Id)) + (' Request No: ') + (str(self.requestNo)) + (' REQUESTING CS') + (EXIT))
            self.send(('Request', self.process_Id, self.RN[self.process_Id]), self.reqProcess)
        self._label_('await')
        while (not (self.HavePrivilege == True)):
            self._process_event(self._event_patterns, True, None)
        self._label_('cs')
        task()
        self._label_('release')
        self.output(LEAVING + ('Process Id: ') + (str(self.process_Id)) + (' Request No: ') + (str(self.requestNo)) + (' LEAVING CS') + (EXIT))
        self.LN[self.process_Id] = self.RN[self.process_Id]
        for process in self.reqProcess:
            if ((not (process in self.Q)) and (self.RN[process] == self.LN[process] + (1))):
                self.Q.append(process)
        if self.Q:
            self.HavePrivilege = False
            tempQ = self.Q
            headQ = tempQ.pop(0)
            try:
                self.send(('Privilege', tempQ, self.LN), headQ)
            except ImportError:
                from queue import Queue
        self.Requesting = False

    def main(self):

        def anounce():
            self.output(ENTERING + ('Process Id: ') + (str(self.process_Id)) + (' Request No: ') + (str(self.requestNo)) + (' ENTERING CS') + (EXIT))
        for i in range(1, self.requestCount + (1)):
            self.requestNo = i
            self.cs(anounce)
        self._label_('await')
        while (not (self.HavePrivilege == False)):
            self._process_event(self._event_patterns, True, None)

    def _event_handler_0(self, fprocess_Id, fReqNo, _timestamp, _source):
        self.RN[fprocess_Id] = max(self.RN[fprocess_Id], fReqNo)
        if (self.HavePrivilege and (not self.Requesting) and (self.RN[fprocess_Id] == self.LN[fprocess_Id] + (1))):
            self.HavePrivilege = False
            try:
                self.send(('Privilege', self.Q, self.LN), fprocess_Id)
            except ImportError:
                from queue import Queue

    def _event_handler_1(self, fQ, fLN, _timestamp, _source):
        self.Q = fQ
        self.LN = fLN
        self.HavePrivilege = True