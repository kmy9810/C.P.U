import datetime # 작성 시간 기록을 위한 패키지
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, app
import bcrypt as bc # 암호화 패키지
client = MongoClient("mongodb+srv://sparta:test@cluster0.280f8z1.mongodb.net/?retryWrites=true&w=majority")
db = client.dbsparta

app = Flask(__name__)

##########################################
#########여기서 부터: 김미영 작성###########
##########################################

@app.route('/')#메인페이지
def home():
    return render_template('index.html')

@app.route('/egg')
def egg():
    return render_template('egg.html')

# #버킷리스트 저장
@app.route("/list/<team_name_id>", methods=["POST"])
def save_content(team_name_id):
    team_name_receive = team_name_id
    content_receive = request.form['content_give']
    star_receive = request.form['star_give']
    emo_receive = request.form['emo_give']
    name_receive = request.form['name_give']
    num_list = list(db.contentDB.find({},{'_id':False}))
    num = 1
    if num_list:
        num = num_list[-1]['num']+1
    print(num)
    
    if content_receive =="" :
        return jsonify({ 'result': 'fail_00', 'msg': '버킷 내용을 작성해 주세요!'})
    if star_receive =="--선택하기--" :
        return jsonify({ 'result': 'fail_01', 'msg': '중요도를 선택 해주세요!'})
    if name_receive =="" :
        return jsonify({ 'result': 'fail_02', 'msg': '이름을 작성해 주세요!'})
    if emo_receive =="--선택하기--" :
        return jsonify({ 'result': 'fail_02', 'msg': '이모지를 작성해 주세요!'})

    doc = {
        'num' : num,
        'team_name' : team_name_receive,
        'content' : content_receive,
        'star' : star_receive,
        'emo' : emo_receive,
        'name' : name_receive,
        'date' : datetime.datetime.now(),
        'done' : 0
    }
    
    db.contentDB.insert_one(doc)
    print(doc) 
    return jsonify({'msg':'버킷리스트가 생성되었습니다.'})



#버킷 불러오기
@app.route("/list/<team_name_id>/data", methods=["GET"])
def show_content(team_name_id):
    team_name_receive = team_name_id
    all_contents = list(db.contentDB.find({'team_name':team_name_receive},{'_id':False}))[::-1]
    
    all_done = len(list(db.contentDB.find({'team_name':team_name_receive, 'done':1},{'_id':False}))[::-1])
    print(all_done)

    
    return jsonify({'result':all_contents, 'total_done':all_done})
#버킷리스트 삭제
@app.route("/list/<team_name_id>", methods=["DELETE"])
def delete_content(team_name_id):
    num_receive = request.form['num_give']
    print(num_receive)
    db.contentDB.delete_one({'num':int(num_receive)})
    return jsonify({'msg':'버킷리스트가 삭제되었습니다.'})  
    

#버킷리스트 완료/취소
@app.route("/list/<team_name>", methods=["PUT"])
def put_content(team_name):
    # num_receive = request.form['num_give']
    num_receive = request.form['num_give']
    state_receive= int(request.form['state_give'])
    db.contentDB.update_one({'num': int(num_receive)}, {'$set':{'done':state_receive}}) #num은 문자열로 돌아옴!
    if state_receive:
        return jsonify({'msg':'버킷리스트 달성!', 'done':1})
    else:
        return jsonify({'msg':'버킷리스트 달성 취소', 'done':0})
    
@app.route("/heart", methods=["PUSH"])
def save_heart():
    num_list = list(db.heartDB.find({},{'_id':False}))
    num = int(num_list[0]['heart'])+1
    db.heartDB.update_one({}, {'$set':{'heart':num}})
    print(num)

    return jsonify({'msg':'🦜 고맙다 핑!!!핑핑핑핑피잉핑ㅇ!!!!!!!'})

@app.route("/heart", methods=["GET"])
def show_heart():
    total_heart = list(db.heartDB.find({},{'_id':False}))
    print(total_heart)
    return jsonify({'result':total_heart})
    





##########################################
#########여기서 부터: 최창수 작성###########
##########################################
# def ObjtoStr(table):
#     for row in table:
#         row['_id']=str(row['_id'])
#     return table


@app.route('/create-team')#조 생성 페이지
def create_team():
    return render_template('content1.html')
@app.route('/list/<string:team_name_id>/')#조별 버킷리스트 페이지
def teampage(team_name_id):
    team_name = db.teamDB.find_one({'team_name':team_name_id})
    if team_name is None:
        return '삐빅 잘못된 접근입니다!'
    return render_template('content2.html')
@app.route("/teams", methods=["POST"])#조 생성 API
def post_team():
    team_name_receive = request.form['team_name_give']
    leader_name_receive = request.form['leader_name_give']
    pw_receive=request.form['pw_give']
    hashed_pw=bc.hashpw(pw_receive.encode("utf-8"), bc.gensalt()).decode("utf-8")
    #각 입력값이 비어있을 경우 등록 실패
    if db.teamDB.find_one({'team_name':team_name_receive}) != None:
        return jsonify({ 'result': 'fail_00', 'msg': '이미 존재하는 조이름입니다.'})
    if db.teamDB.find_one({'leader_name':leader_name_receive}) != None:
        return jsonify({ 'result': 'fail_01', 'msg': '이미 존재하는 조장 닉네임입니다.'})
    
    #db저장
    doc = {
        'team_name' : team_name_receive,
        'leader_name' : leader_name_receive,
        'pw' : hashed_pw
    }
    db.teamDB.insert_one(doc)
    return jsonify({ 'result': 'success', 'msg': '조가 생성되었습니다.'})

@app.route("/teams", methods=["GET"]) #조 표시 API
def get_team():
    #DB로 부터 비밀번호를 제외한 데이터 불러오기
    team_data = list(db.teamDB.find({},{'_id':False,'pw':False,}))
    return jsonify({'result':team_data})

@app.route("/teams/<string:team_name_id>",methods=["DELETE"])# 조 데이터 삭제 API
def delete_team(team_name_id):
    #프론트로부터 받을 데이터들
    input_leader_name_receive = request.form['input_leader_name_give']
    input_pw_receive=request.form['input_pw_give']
    #존재하지 않는 ID(닉네임), ID불일치 확인
    if not list(db.teamDB.find({'leader_name':input_leader_name_receive},{})):
        return jsonify({ 'result': 'fail', 'msg': '옳지않은 ID 혹은 PW입니다.'})
    team = db.teamDB.find_one({'team_name':team_name_id, 'leader_name':input_leader_name_receive})
    if team == None:
        return jsonify({ 'result': 'fail', 'msg': '옳지않은 ID 혹은 PW입니다.'})
    #데이터 가져오고, 비밀번호 비교
    hashed_pw=team['pw']
    if not bc.checkpw(input_pw_receive.encode("utf-8"),hashed_pw.encode("utf-8")):
        return jsonify({ 'result': 'fail', 'msg': '옳지않은 ID 혹은 PW입니다.'})
    #데이터 삭제
    db.teamDB.delete_one({'team_name':team['team_name'], 'leader_name':team['leader_name']})
    db.contentDB.delete_many({'team_name':team['team_name']})
    return  jsonify({ 'result': 'success', 'msg': '조의 모든 데이터가 삭제되었습니다.'})

@app.route("/rank", methods=["GET"]) #랭킹
def rank_team():
    #각 DB로 부터 데이터 불러오기
    team_data = list(db.teamDB.find({},{'team_name':True,}))
    list_data = list(db.contentDB.find({},{'team_name':True,'done':True,'star':True,}))
    team_name_dict=dict()
    #점수집계
    '''
    score1: 각 버킷리스트마다 기본점수로 5*(중요도), 완료된 버킷리스트의 경우 10배로 적용
    score2: 완료된 버킷리스트만 집계. 각 50*(중요도) 
    '''
    for team in team_data:
        team_name_dict[team['team_name']]=[0,0]
    for i in list_data:
        team=i['team_name']
        done=int(i['done'])
        score1= (5*(done^1) + done*50)*len(i['star'])
        score2= done*50*len(i['star'])
        team_name_dict[team][0]+=score1
        team_name_dict[team][1]+=score2
    #table화
    result=list()
    for t in team_data:
        team_name=t['team_name']
        result.append({'team_name':team_name, 'score1':team_name_dict[team_name][0],'score2':team_name_dict[team_name][1]})
    sort_by_s1=sorted(result, reverse=True, key=(lambda x:x['score1']))
    sort_by_s2=sorted(result, reverse=True, key=(lambda x:x['score2']))
    return jsonify({'result1':sort_by_s1,'result2':sort_by_s2})



if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)

