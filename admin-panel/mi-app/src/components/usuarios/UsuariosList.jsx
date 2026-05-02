import React, { useState, useEffect } from 'react';
import { usuariosService } from '../../services/usuariosService';
import UsuarioForm from './UsuarioForm';
import './UsuariosList.css';

const UsuariosList = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUsuario, setEditingUsuario] = useState(null);

  useEffect(() => {
    loadUsuarios();
  }, []);

  const loadUsuarios = async () => {
    try {
      const data = await usuariosService.getUsuarios();
      setUsuarios(data);
    } catch (error) {
      console.error('Error cargando usuarios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingUsuario(null);
    setShowModal(true);
  };

  const handleEdit = (usuario) => {
    setEditingUsuario(usuario);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este usuario?')) {
      try {
        await usuariosService.deleteUsuario(id);
        await loadUsuarios();
      } catch (error) {
        console.error('Error eliminando usuario:', error);
      }
    }
  };

  const handleSubmit = async (usuarioData) => {
    console.log('1. handleSubmit llamado con datos:', usuarioData);
    try {
      if (editingUsuario) {
        console.log('2. Editando usuario existente');
        await usuariosService.updateUsuario(editingUsuario.id_usuario, usuarioData);
      } else {
        console.log('2. Creando nuevo usuario');
        await usuariosService.createUsuario(usuarioData);
      }
      console.log('3. Operación exitosa, cerrando modal');
      setShowModal(false);
      await loadUsuarios();
      console.log('4. Lista recargada');
    } catch (error) {
      console.error('ERROR en handleSubmit:', error);
    }
  };

  const getRolBadgeClass = (rol) => {
    switch (rol) {
      case 'admin':
        return 'bg-danger';
      case 'usuario':
        return 'bg-primary';
      case 'empleado':
        return 'bg-warning text-dark';
      default:
        return 'bg-secondary';
    }
  };

  if (loading) return <div className="text-center p-4">Cargando usuarios...</div>;

  return (
    <div className="usuarios-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">👥 Gestión de Usuarios</h2>
        <button 
          className="btn btn-primary"
          onClick={handleCreate}
        >
          ➕ Nuevo Usuario
        </button>
      </div>

      <div className="table-responsive">
        <table className="table table-striped table-hover table-bordered">
          <thead className="table-dark">
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th>Rol</th>
              <th className="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center text-muted py-4">
                  No hay usuarios registrados
                </td>
              </tr>
            ) : (
              usuarios.map(usuario => (
                <tr key={usuario.id_usuario}>
                  <td className="fw-bold">{usuario.id_usuario}</td>
                  <td>{usuario.nombre}</td>
                  <td>{usuario.email}</td>
                  <td>{usuario.telefono || 'N/A'}</td>
                  <td>
                    <span className={`badge ${getRolBadgeClass(usuario.rol)}`}>
                      {usuario.rol}
                    </span>
                  </td>
                  <td className="text-center">
                    <div className="btn-group" role="group">
                      <button 
                        className="btn btn-warning btn-sm me-1"
                        onClick={() => handleEdit(usuario)}
                        title="Editar usuario"
                      >
                        ✏️ Editar
                      </button>
                      <button 
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(usuario.id_usuario)}
                        title="Eliminar usuario"
                      >
                        🗑️ Eliminar
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
        <UsuarioForm
          usuario={editingUsuario}
          onSubmit={handleSubmit}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default UsuariosList;