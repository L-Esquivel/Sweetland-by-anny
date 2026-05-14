import React, { useState } from 'react';
import { platformService } from '../../services/platformService';

function SupportModal({ show, onClose }) {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ message: '', type: '' });

  if (!show) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setNotification({ message: '', type: '' });
    try {
      const response = await platformService.contactSupport({ subject, message });
      setNotification({ message: response.mensaje, type: 'success' });
      setSubject('');
      setMessage('');
      setTimeout(() => {
        onClose();
        setNotification({ message: '', type: '' });
      }, 3000);
    } catch (error) {
      setNotification({ message: error.message, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }} tabIndex="-1">
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Contactar a Soporte</h5>
            <button type="button" className="btn-close" onClick={onClose} disabled={loading}></button>
          </div>
          <div className="modal-body">
            {notification.message && (
              <div className={`alert ${notification.type === 'success' ? 'alert-success' : 'alert-danger'}`}>
                {notification.message}
              </div>
            )}
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="support-subject" className="form-label">Asunto</label>
                <input type="text" className="form-control" id="support-subject" value={subject} onChange={(e) => setSubject(e.target.value)} required />
              </div>
              <div className="mb-3">
                <label htmlFor="support-message" className="form-label">Describe tu consulta o problema:</label>
                <textarea className="form-control" id="support-message" rows="5" value={message} onChange={(e) => setMessage(e.target.value)} required></textarea>
              </div>
              <div className="modal-footer border-0">
                <button type="submit" className="btn btn-primary w-100" disabled={loading}>{loading ? 'Enviando...' : 'Enviar Solicitud'}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SupportModal;