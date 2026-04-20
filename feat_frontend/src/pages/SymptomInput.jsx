import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import './SymptomInput.css';

const SITUATIONS = [
  { val: 'before_exercise', label: '운동 전에' },
  { val: 'during_exercise', label: '운동 중에' },
  { val: 'after_exercise', label: '운동 후에' },
  { val: 'daily', label: '일상에서' },
  { val: 'other', label: '기타' },
];

const SYMPTOM_CHIPS = [
  '뻐근하고 뻣뻣해요',
  '무릎 앞쪽이 아파요',
  '무릎 바깥쪽이 아파요',
  '불안정한 느낌이에요',
  '예방 목적이에요',
  '직접 설명할게요',
];

export default function SymptomInput() {
  const navigate = useNavigate();
  const { session, updateSession } = useSession();

  const [step, setStep] = useState(1);
  const [situation, setSituation] = useState(null);
  const [situationLabel, setSituationLabel] = useState(null);
  const [inputText, setInputText] = useState('');
  const [shakeInput, setShakeInput] = useState(false);
  const [messages, setMessages] = useState([]);
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  function pickSituation(sit) {
    setSituation(sit.val);
    setSituationLabel(sit.label);
  }

  function goToSymptom() {
    updateSession({ situation });
    setStep(2);
  }

  function pickSymptomChip(text) {
    setTimeout(() => sendSymptom(text), 180);
  }

  function sendSymptom(text) {
    const msg = (text ?? inputText).trim();
    if (!msg) {
      setShakeInput(true);
      setTimeout(() => setShakeInput(false), 400);
      return;
    }
    updateSession({ symptom: msg });
    setMessages((prev) => [...prev, { role: 'user', text: msg }, { role: 'typing' }]);
    setInputText('');
    setTimeout(() => {
      setMessages((prev) => prev.filter((m) => m.role !== 'typing'));
      navigate('/consent');
    }, 1500);
  }

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => step === 1 ? navigate('/1') : setStep(1)}>
          <svg className="ic" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
        </button>
        <div className="title">증상 입력</div>
      </div>

      {step === 1 ? (
        <>
          <div className="content chat-pane">
            <div className="bubble-bot">{`${session.part || '무릎'}이 불편하시군요.\n언제 불편하세요?`}</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}>
              {SITUATIONS.map((sit) => (
                <button
                  key={sit.val}
                  className={`chip ${situation === sit.val ? 'selected' : ''}`}
                  onClick={() => pickSituation(sit)}
                >
                  {sit.label}
                </button>
              ))}
            </div>
            {situationLabel && (
              <>
                <div className="bubble-user">{situationLabel}</div>
                <div className="bubble-bot">알겠어요. 다음 단계로 넘어갈까요?</div>
              </>
            )}
          </div>
          <div className="bottombar">
            <button className="btn btn-primary" disabled={!situation} onClick={goToSymptom}>
              다음으로 넘어갈게요
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="content chat-pane" ref={chatRef}>
            <div className="bubble-bot">어떤 느낌인지 알려주세요</div>
            <div className="symptom-chips">
              {SYMPTOM_CHIPS.map((chip) => (
                <button key={chip} className="chip" onClick={() => pickSymptomChip(chip)}>
                  {chip}
                </button>
              ))}
            </div>
            {messages.map((m, i) =>
              m.role === 'typing' ? (
                <div key={i} className="typing"><span /><span /><span /></div>
              ) : (
                <div key={i} className={`bubble-${m.role}`}>{m.text}</div>
              )
            )}
          </div>
          <div className="bottombar">
            <div className={`chat-input ${shakeInput ? 'shake' : ''}`}>
              <input
                type="text"
                placeholder="자세히 입력해주세요"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendSymptom()}
              />
              <button className="send" onClick={() => sendSymptom()}>
                <svg className="ic ic-sm" viewBox="0 0 24 24" style={{ stroke: '#fff' }}>
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" fill="#fff" stroke="#fff" />
                </svg>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
