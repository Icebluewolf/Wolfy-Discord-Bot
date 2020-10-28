class Parse:
  alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

  def __init__(self, sourceString):
    self.string = sourceString
    self.parse = Parse.makeParsed(sourceString)

  def makeParsed(inpStr):
    strList = [""]
    strListIndex = 0
    lastOneAlpha = False
    inQuotes = False
    for char in inpStr:
      isAlpha = False
      if char == '$' or char == '"':
        inQuotes = not inQuotes
        if lastOneAlpha:
          strListIndex += 1
          strList.append("")
          lastOneAlpha = False
        continue
      if inQuotes:
        strList[strListIndex] += char
        lastOneAlpha = True
        continue
      for alpha in Parse.alphabet:
        if char == alpha:
          isAlpha = True
          break
      if (not isAlpha) and lastOneAlpha:
        strListIndex += 1
        strList.append("")
        lastOneAlpha = False
      elif isAlpha:
        lastOneAlpha = True
        strList[strListIndex] += char
    if not lastOneAlpha:
      strList.pop()
    return(strList)

  def checkSubset(sub, sup):
    for S in range(len(sup.parse)):
      subFits = True
      for s in range(len(sub.parse)):
        if sup.parse[S+s] != sub.parse[s]:
          subFits = False
          break
      if subFits:
        return(True, S)
    return(False, None)

class Task:
  container = []

  def __init__(self, call: Parse, task, argNum):
    self.call = call
    self.task = task
    self.argNum = argNum
    Task.container.append(self)
  
  def eval(self, triedCall: Parse):
    subSet, startLine = Parse.checkSubset(self.call, triedCall)
    if subSet:
      try:
        args = []
        for i in range(self.argNum):
          args.append(triedCall.parse[len(self.call.parse)+i+startLine])
        self.task(args)
        return(True)
      except:
        print("ERROR")
      return(False)
    
  def evalAll(triedCall: Parse):
    for task in Task.container:
      if task.eval(triedCall):
        return

class CallBack(Task):
  def __init__(self, call: Parse, response: str):
    def callBackFunction(args):
      print(response)
    super().__init__(call, callBackFunction, 0)
