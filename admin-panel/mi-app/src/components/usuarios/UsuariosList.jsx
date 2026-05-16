import React, { useState, useEffect } from 'react';
import { usuariosService } from '../../services/usuariosService';
import UserForm from './UsuarioForm';
import './UsuariosList.css';

const UsuariosList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await usuariosService.getUsers();
      setUsers(data);
    } catch (error) {
      console.error('Error loading users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingUser(null);
    setShowModal(true);
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await usuariosService.deleteUser(id);
        await loadUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const handleSubmit = async (userData) => {
    console.log('1. handleSubmit called with data:', userData);
    try {
      if (editingUser) {
        console.log('2. Editing existing user');
        await usuariosService.updateUser(editingUser.id_usuario, userData);
      } else {
        console.log('2. Creating new user');
        await usuariosService.createUser(userData);
      }
      console.log('3. Operation successful, closing modal');
      setShowModal(false);
      await loadUsers();
      console.log('4. List reloaded');
    } catch (error) {
      console.error('ERROR en handleSubmit:', error);
    }
  };

  const getRoleBadgeClass = (rol) => {
    switch (rol) {
      case 'admin':
        return 'bg-danger';
      case 'cliente':
        return 'bg-primary';
      case 'empleado':
        return 'bg-warning text-dark';
      default:
        return 'bg-secondary';
    }
  };

  if (loading) return <div className="text-center p-4">Loading users...</div>;

  return (
    <div className="usuarios-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">👥 User Management</h2>
        <button 
          className="btn btn-primary"
          onClick={handleCreate}
        >
          ➕ New User
        </button>
      </div>

      <div className="table-responsive">
        <table className="table table-striped table-hover table-bordered">
          <thead className="table-dark">
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Role</th>
              <th className="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center text-muted py-4">
                  No users registered yet
                </td>
              </tr>
            ) : (
              users.map(user => (
                <tr key={user.id_usuario}>
                  <td className="fw-bold">{user.id_usuario}</td>
                  <td>{user.nombre}</td>
                  <td>{user.email}</td>
                  <td>{user.telefono || 'N/A'}</td>
                  <td>
                    <span className={`badge ${getRoleBadgeClass(user.rol)}`}>
                      {user.rol}
                    </span>
                  </td>
                  <td className="text-center">
                    <div className="btn-group" role="group">
                      <button 
                        className="btn btn-warning btn-sm me-1"
                        onClick={() => handleEdit(user)}
                        title="Edit user"
                      >
                        ✏️ Edit
                      </button>
                      <button 
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(user.id_usuario)}
                        title="Delete user"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <UserForm
          user={editingUser}
          onSubmit={handleSubmit}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default UsuariosList;