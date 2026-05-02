import { useState } from 'react';

const Register = ({ onShowLogin }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    password: '',
    telefono: '',
    direccion: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/auth/registrarse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Registro exitoso. Ahora puedes iniciar sesión.');
        onShowLogin();
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Error en el registro');
      }
    } catch (err) {
      setError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0d6efd',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px'
      }}>
        {/* Mensaje de bienvenida */}
        <div style={{
          textAlign: 'center',
          color: 'white',
          marginBottom: '40px'
        }}>
          <h1 style={{ 
            fontWeight: 'bold', 
            marginBottom: '20px',
            fontSize: '2.5rem'
          }}>
            🎂 Sweetland
          </h1>
          <p style={{ 
            fontSize: '1.2rem',
            opacity: 0.9,
            marginBottom: '5px'
          }}>
            Crear cuenta nueva
          </p>
          <p style={{ 
            fontSize: '0.9rem',
            opacity: 0.7
          }}>
            Únete al sistema Sweetland By Amy
          </p>
        </div>

        {/* Card de registro */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '30px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
        }}>
          <h4 style={{
            textAlign: 'center',
            marginBottom: '25px',
            color: '#333'
          }}>
            Registro de Usuario
          </h4>
          
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '15px' }}>
              <input
                type="text"
                name="nombre"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
                placeholder="Nombre completo"
                value={formData.nombre}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            
            <div style={{ marginBottom: '15px' }}>
              <input
                type="email"
                name="email"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
                placeholder="Correo electrónico"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            
            <div style={{ marginBottom: '15px' }}>
              <input
                type="password"
                name="password"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
                placeholder="Contraseña"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            
            <div style={{ marginBottom: '15px' }}>
              <input
                type="text"
                name="telefono"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
                placeholder="Teléfono (opcional)"
                value={formData.telefono}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <input
                type="text"
                name="direccion"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem'
                }}
                placeholder="Dirección (opcional)"
                value={formData.direccion}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
            
            <button 
              type="submit" 
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: loading ? '#6c757d' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '1rem',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
              disabled={loading}
            >
              {loading ? 'Registrando...' : '✅ Registrarse'}
            </button>
          </form>

          {error && (
            <div style={{
              backgroundColor: '#f8d7da',
              color: '#721c24',
              padding: '10px',
              borderRadius: '6px',
              marginTop: '20px',
              textAlign: 'center',
              fontSize: '0.9rem'
            }}>
              {error}
            </div>
          )}

          <div style={{
            textAlign: 'center',
            marginTop: '20px',
            paddingTop: '20px',
            borderTop: '1px solid #eee'
          }}>
            <small style={{ color: '#666' }}>
              ¿Ya tienes cuenta?{' '}
              <button 
                onClick={onShowLogin}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#0d6efd',
                  textDecoration: 'underline',
                  cursor: 'pointer'
                }}
                disabled={loading}
              >
                Iniciar Sesión
              </button>
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;