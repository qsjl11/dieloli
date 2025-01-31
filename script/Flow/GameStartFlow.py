from script.Design import GameTime,AttrCalculation,CharacterHandle,MapHandle,Course,Interest
from script.Core import CacheContorl
from script.Panel import SeeCharacterAttrPanel

def initGameStart():
    '''
    用于结束角色创建正式开始游戏的初始化流程
    '''
    GameTime.initTime()
    AttrCalculation.setAttrOver('0')
    Course.initPhaseCourseHour()
    CharacterHandle.initCharacterList()
    Interest.initCharacterInterest()
    Course.initCharacterKnowledge()
    Course.initClassTeacher()
    Course.initClassTimeTable()
    SeeCharacterAttrPanel.initShowAttrPanelList()
    characterPosition = CacheContorl.characterData['character']['0']['Position']
    MapHandle.characterMoveScene(['0'],characterPosition,'0')
    CacheContorl.nowFlowId = 'main'
