from sdv.imagegeneration.farm import generateFarm
from sdv.farmInfo import getFarmInfo
from sdv.playerInfo import playerInfo
from sdv.savefile import savefile

save = savefile('emi')
farm = getFarmInfo(save)
generateFarm('spring', farm).show()