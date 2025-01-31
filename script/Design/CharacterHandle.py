import random
import math
import datetime
from script.Core import CacheContorl,ValueHandle,GameData,TextLoading,GamePathConfig,GameConfig
from script.Design import AttrCalculation,MapHandle,AttrText

language = GameConfig.language
gamepath = GamePathConfig.gamepath
featuresList = AttrCalculation.getFeaturesList()
sexList = list(TextLoading.getTextData(TextLoading.rolePath, 'Sex'))
ageTemList = list(TextLoading.getTextData(TextLoading.attrTemplatePath,'AgeTem'))
characterList = list(GameData._gamedata[language]['character'].keys())

def initCharacterList():
    '''
    初始生成所有npc数据
    '''
    initCharacterTem()
    i = 1
    for character in CacheContorl.npcTemData:
        initCharacter(i,character)
        i += 1
    initCharacterDormitory()
    initCharacterPosition()

def initCharacter(nowId:str,character:dict):
    '''
    按id生成角色属性
    Keyword arguments:
    nowId -- 角色id
    character -- 角色生成模板数据
    '''
    AttrCalculation.initTemporaryCharacter()
    characterId = str(nowId)
    CacheContorl.characterData['character'][characterId] = CacheContorl.temporaryCharacter.copy()
    AttrCalculation.setDefaultCache()
    characterName = character['Name']
    characterSex = character['Sex']
    CacheContorl.characterData['character'][characterId]['Sex'] = characterSex
    defaultAttr = AttrCalculation.getAttr(characterSex)
    defaultAttr['Name'] = characterName
    defaultAttr['Sex'] = characterSex
    AttrCalculation.setSexCache(characterSex)
    defaultAttr['Features'] = CacheContorl.featuresList.copy()
    if 'MotherTongue' in character:
        defaultAttr['Language'][character['MotherTongue']] = 10000
        defaultAttr['MotherTongue'] = character['MotherTongue']
    else:
        defaultAttr['Language']['Chinese'] = 10000
    if 'Age' in character:
        ageTem = character['Age']
        characterAge = AttrCalculation.getAge(ageTem)
        defaultAttr['Age'] = characterAge
        characterAgeFeatureHandle(ageTem,characterSex)
        defaultAttr['Features'] = CacheContorl.featuresList.copy()
    elif 'Features' in character:
        AttrCalculation.setAddFeatures(character['Features'])
        defaultAttr['Features'] = CacheContorl.featuresList.copy()
    if 'Features' in character:
        height = AttrCalculation.getHeight(characterSex, defaultAttr['Age'],character['Features'])
    else:
        height = AttrCalculation.getHeight(characterSex, defaultAttr['Age'],{})
    defaultAttr['Height'] = height
    if 'Weight' in character:
        weightTemName = character['Weight']
    else:
        weightTemName = 'Ordinary'
    if 'BodyFat' in character:
        bodyFatTem = character['BodyFat']
    else:
        bodyFatTem = weightTemName
    bmi = AttrCalculation.getBMI(weightTemName)
    weight = AttrCalculation.getWeight(bmi, height['NowHeight'])
    defaultAttr['Weight'] = weight
    if defaultAttr['Age'] <= 18 and defaultAttr['Age'] >= 7:
        classGrade = str(defaultAttr['Age'] - 6)
        defaultAttr['Class'] = random.choice(CacheContorl.placeData["Classroom_" + classGrade])
    bodyFat = AttrCalculation.getBodyFat(characterSex,bodyFatTem)
    measurements = AttrCalculation.getMeasurements(characterSex, height['NowHeight'], weight,bodyFat,bodyFatTem)
    defaultAttr['Measirements'] = measurements
    defaultAttr['Knowledge'] = {}
    CacheContorl.temporaryCharacter.update(defaultAttr)
    CacheContorl.featuresList = {}
    CacheContorl.characterData['character'][characterId] = CacheContorl.temporaryCharacter.copy()
    CacheContorl.temporaryCharacter = CacheContorl.temporaryCharacterBak.copy()

def characterAgeFeatureHandle(ageTem:str,characterSex:str):
    '''
    按年龄模板生成角色特性数据
    Keyword arguments:
    ageTem -- 年龄模板
    characterSex -- 角色性别
    '''
    if ageTem == 'SchoolAgeChild':
        if characterSex == sexList[0]:
            CacheContorl.featuresList['Age'] = featuresList["Age"][0]
        elif characterSex == sexList[1]:
            CacheContorl.featuresList['Age'] = featuresList["Age"][1]
        else:
            CacheContorl.featuresList['Age'] = featuresList["Age"][2]
    elif ageTem == 'OldAdult':
        CacheContorl.featuresList['Age'] = featuresList["Age"][3]

def initCharacterTem():
    '''
    初始化角色模板数据
    '''
    npcData = getRandomNpcData()
    nowCharacterList = characterList.copy()
    npcData += [getDirCharacterTem(character) for character in nowCharacterList]
    CacheContorl.npcTemData = npcData

def getDirCharacterTem(character:str) -> dict:
    '''
    获取预设角色模板数据
    '''
    return TextLoading.getCharacterData(character)['AttrTemplate']

randomNpcMax = int(GameConfig.random_npc_max)
randomTeacherProportion = int(GameConfig.proportion_teacher)
randomStudentProportion = int(GameConfig.proportion_student)
ageWeightData = {
    "Teacher":randomTeacherProportion,
    "Student":randomStudentProportion
}
ageWeightReginData = ValueHandle.getReginList(ageWeightData)
ageWeightReginList = list(map(int,ageWeightReginData.keys()))
def getRandomNpcData() -> list:
    '''
    生成所有随机npc的数据模板
    '''
    if CacheContorl.randomNpcList == []:
        ageWeightMax = 0
        for i in ageWeightData:
            ageWeightMax += int(ageWeightData[i])
        for i in range(0,randomNpcMax):
            nowAgeWeight = random.randint(-1,ageWeightMax - 1)
            nowAgeWeightRegin = ValueHandle.getNextValueForList(nowAgeWeight,ageWeightReginList)
            ageWeightTem = ageWeightReginData[str(nowAgeWeightRegin)]
            randomNpcSex = getRandNpcSex()
            randomNpcName = AttrText.getRandomNameForSex(randomNpcSex)
            randomNpcAgeTem = getRandNpcAgeTem(ageWeightTem)
            fatTem = getRandNpcFatTem(ageWeightTem)
            bodyFatTem = getRandNpcBodyFatTem(ageWeightTem,fatTem)
            randomNpcNewData = {
                "Name":randomNpcName,
                "Sex":randomNpcSex,
                "Age":randomNpcAgeTem,
                "Position":["0"],
                "AdvNpc":"1",
                "Weight":fatTem,
                "BodyFat":bodyFatTem
            }
            CacheContorl.randomNpcList.append(randomNpcNewData)
        return CacheContorl.randomNpcList

sexWeightData = TextLoading.getTextData(TextLoading.attrTemplatePath,'RandomNpcSexWeight')
sexWeightMax = 0
for i in sexWeightData:
    sexWeightMax += int(sexWeightData[i])
sexWeightReginData = ValueHandle.getReginList(sexWeightData)
sexWeightReginList = list(map(int,sexWeightReginData.keys()))
def getRandNpcSex() -> str:
    '''
    随机获取npc性别
    '''
    nowWeight = random.randint(0,sexWeightMax - 1)
    weightRegin = ValueHandle.getNextValueForList(nowWeight,sexWeightReginList)
    return sexWeightReginData[str(weightRegin)]

fatWeightData = TextLoading.getTextData(TextLoading.attrTemplatePath,'FatWeight')
def getRandNpcFatTem(agejudge:str) -> str:
    '''
    按人群年龄段体重分布比例随机生成体重模板
    Keyword arguments:
    agejudge -- 年龄段
    '''
    nowFatWeightData = fatWeightData[agejudge]
    nowFatTem = ValueHandle.getRandomForWeight(nowFatWeightData)
    return nowFatTem

bodyFatWeightData = TextLoading.getTextData(TextLoading.attrTemplatePath,'BodyFatWeight')
def getRandNpcBodyFatTem(ageJudge:str,bmiTem:str) -> str:
    '''
    按年龄段体脂率分布比例随机生成体脂率模板
    Keyword arguments:
    ageJudge -- 年龄段
    bmiTem -- bmi模板
    '''
    nowBodyFatData = bodyFatWeightData[ageJudge][bmiTem]
    return ValueHandle.getRandomForWeight(nowBodyFatData)

ageTemWeightData = TextLoading.getTextData(TextLoading.attrTemplatePath,'AgeWeight')
def getRandNpcAgeTem(agejudge:str) -> int:
    '''
    按年龄断随机生成npc年龄
    Keyword arguments:
    ageJudge -- 年龄段
    '''
    nowAgeWeightData  = ageTemWeightData[agejudge]
    nowAgeTem = ValueHandle.getRandomForWeight(nowAgeWeightData)
    return nowAgeTem

def getCharacterIndexMax() -> int:
    '''
    获取角色数量
    '''
    characterData = CacheContorl.characterData['character']
    characterDataMax = len(characterData.keys()) - 1
    return characterDataMax

def getCharacterIdList() -> list:
    '''
    获取角色id列表
    '''
    characterData = CacheContorl.characterData['character']
    return list(characterData.keys())

def initCharacterDormitory():
    '''
    分配角色宿舍
    小于18岁，男生分配到男生宿舍，女生分配到女生宿舍，按宿舍楼层和角色年龄，从下往上，从小到大分配，其他性别分配到地下室，大于18岁，教师宿舍混居
    '''
    characterData = {}
    characterSexData = {
        "Man":{},
        "Woman":{},
        "Other":{},
        "Teacher":{}
    }
    for character in CacheContorl.characterData['character']:
        if CacheContorl.characterData['character'][character]['Age'] < 18:
            if CacheContorl.characterData['character'][character]['Sex'] in ['Man','Woman']:
                characterSexData[CacheContorl.characterData['character'][character]['Sex']][character] = CacheContorl.characterData['character'][character]['Age']
            else:
                characterSexData['Other'][character] = CacheContorl.characterData['character'][character]['Age']
        else:
            characterSexData['Teacher'][character] = CacheContorl.characterData['character'][character]['Age']
    manMax = len(characterSexData['Man'])
    womanMax = len(characterSexData['Woman'])
    otherMax = len(characterSexData['Other'])
    teacherMax = len(characterSexData['Teacher'])
    characterSexData['Man'] = [k[0] for k in sorted(characterSexData['Man'].items(),key=lambda x:x[1])]
    characterSexData['Woman'] = [k[0] for k in sorted(characterSexData['Woman'].items(),key=lambda x:x[1])]
    characterSexData['Other'] = [k[0] for k in sorted(characterSexData['Other'].items(),key=lambda x:x[1])]
    characterSexData['Teacher'] = [k[0] for k in sorted(characterSexData['Teacher'].items(),key=lambda x:x[1])]
    teacherDormitory = {x:0 for x in sorted(CacheContorl.placeData['TeacherDormitory'],key=lambda x:x[0])}
    maleDormitory = {}
    femaleDormitory = {}
    for key in CacheContorl.placeData:
        if 'FemaleDormitory' in key:
            femaleDormitory[key] = CacheContorl.placeData[key]
        elif 'MaleDormitory' in key:
            maleDormitory[key] = CacheContorl.placeData[key]
    maleDormitory = {x:0 for j in [k[1] for k in sorted(maleDormitory.items(),key=lambda x:x[0])] for x in j}
    femaleDormitory = {x:0 for j in [k[1] for k in sorted(femaleDormitory.items(),key=lambda x:x[0])] for x in j}
    basement = {x:0 for x in CacheContorl.placeData['Basement']}
    maleDormitoryMax = len(maleDormitory.keys())
    femaleDormitoryMax = len(femaleDormitory.keys())
    teacherDormitoryMax = len(teacherDormitory)
    basementMax = len(basement)
    singleRoomMan = math.ceil(manMax / maleDormitoryMax)
    singleRoomWoman = math.ceil(womanMax / femaleDormitoryMax)
    singleRoomBasement = math.ceil(otherMax / basementMax)
    singleRoomTeacher = math.ceil(teacherMax / teacherDormitoryMax)
    for character in characterSexData['Man']:
        nowRoom = list(maleDormitory.keys())[0]
        CacheContorl.characterData['character'][character]['Dormitory'] = nowRoom
        maleDormitory[nowRoom] += 1
        if maleDormitory[nowRoom] >= singleRoomMan:
            del maleDormitory[nowRoom]
    for character in characterSexData['Woman']:
        nowRoom = list(femaleDormitory.keys())[0]
        CacheContorl.characterData['character'][character]['Dormitory'] = nowRoom
        femaleDormitory[nowRoom] += 1
        if femaleDormitory[nowRoom] >= singleRoomWoman:
            del femaleDormitory[nowRoom]
    for character in characterSexData['Other']:
        nowRoom = list(basement.keys())[0]
        CacheContorl.characterData['character'][character]['Dormitory'] = nowRoom
        basement[nowRoom] += 1
        if basement[nowRoom] >= singleRoomBasement:
            del basement[nowRoom]
    for character in characterSexData['Teacher']:
        nowRoom = list(teacherDormitory.keys())[0]
        CacheContorl.characterData['character'][character]['Dormitory'] = nowRoom
        teacherDormitory[nowRoom] += 1
        if teacherDormitory[nowRoom] >= singleRoomTeacher:
            del teacherDormitory[nowRoom]

def initCharacterPosition():
    '''
    初始化角色位置
    '''
    for character in CacheContorl.characterData['character']:
        characterPosition = CacheContorl.characterData['character'][character]['Position']
        characterDormitory = CacheContorl.characterData['character'][character]['Dormitory']
        characterDormitory = MapHandle.getMapSystemPathForStr(characterDormitory)
        MapHandle.characterMoveScene(characterPosition,characterDormitory,character)
