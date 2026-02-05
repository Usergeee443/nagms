from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Goal, Plan
from datetime import datetime

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('', methods=['GET'])
@jwt_required()
def get_goals():
    """Barcha maqsadlarni qaytaradi"""
    goals = Goal.query.order_by(Goal.created_at.desc()).all()
    return jsonify([goal.to_dict() for goal in goals]), 200

@goals_bp.route('', methods=['POST'])
@jwt_required()
def create_goal():
    """Yangi maqsad yaratadi"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('start_date') or not data.get('end_date'):
        return jsonify({'error': 'Name, start_date va end_date kiritilishi shart'}), 400
    
    goal = Goal(
        name=data['name'],
        description=data.get('description', ''),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        status=data.get('status', 'planned'),
        progress=data.get('progress', 0)
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify(goal.to_dict()), 201

@goals_bp.route('/<int:goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id):
    """Bitta maqsadni qaytaradi"""
    goal = Goal.query.get_or_404(goal_id)
    return jsonify(goal.to_dict()), 200

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    """Maqsadni yangilaydi"""
    goal = Goal.query.get_or_404(goal_id)
    data = request.get_json()
    
    if data.get('name'):
        goal.name = data['name']
    if data.get('description') is not None:
        goal.description = data['description']
    if data.get('start_date'):
        goal.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('end_date'):
        goal.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if data.get('status'):
        goal.status = data['status']
    if data.get('progress') is not None:
        goal.progress = data['progress']
    
    goal.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(goal.to_dict()), 200

@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    """Maqsadni o'chiradi"""
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    
    return jsonify({'message': 'Maqsad muvaffaqiyatli o\'chirildi'}), 200

# Plans routes
@goals_bp.route('/<int:goal_id>/plans', methods=['GET'])
@jwt_required()
def get_plans(goal_id):
    """Maqsadga bog'langan rejalarni qaytaradi"""
    plans = Plan.query.filter_by(goal_id=goal_id).order_by(Plan.deadline).all()
    return jsonify([plan.to_dict() for plan in plans]), 200

@goals_bp.route('/<int:goal_id>/plans', methods=['POST'])
@jwt_required()
def create_plan(goal_id):
    """Yangi reja yaratadi"""
    goal = Goal.query.get_or_404(goal_id)
    data = request.get_json()
    
    if not data or not data.get('task_name') or not data.get('deadline'):
        return jsonify({'error': 'task_name va deadline kiritilishi shart'}), 400
    
    plan = Plan(
        goal_id=goal_id,
        task_name=data['task_name'],
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date(),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending')
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify(plan.to_dict()), 201

@goals_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    """Rejani yangilaydi"""
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if data.get('task_name'):
        plan.task_name = data['task_name']
    if data.get('deadline'):
        plan.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
    if data.get('priority'):
        plan.priority = data['priority']
    if data.get('status'):
        plan.status = data['status']
    
    plan.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(plan.to_dict()), 200

@goals_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    """Rejani o'chiradi"""
    plan = Plan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({'message': 'Reja muvaffaqiyatli o\'chirildi'}), 200

