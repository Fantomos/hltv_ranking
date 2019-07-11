# -*- coding: utf-8 -*-
import hltvRankingAnalysis as hl
b = hl.HLTVTopsList.getObjectFromFile("data.json")
b.fromFile("data.json")
b.update()
b.save("data.json")
(s,e) = b.getDate()
print(e)