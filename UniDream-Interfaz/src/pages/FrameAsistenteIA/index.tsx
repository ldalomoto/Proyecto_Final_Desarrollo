import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from 'react-router-dom';

// Definimos la estructura de un mensaje
interface Message {
    id: number;
    text: string;
    sender: 'user' | 'bot';
}

export default () => {
    const navigate = useNavigate();
    const messagesEndRef = useRef<HTMLDivElement>(null); // Para auto-scroll

    // --- ESTILOS REUTILIZABLES ---
    const textMenuClass = "text-[#0D0D1B] text-sm transition-colors duration-300 hover:text-[#1213ed] active:text-[#1213ed] cursor-pointer font-medium";
    const buttonPressEffect = "transition-transform duration-100 active:scale-95";

    // --- ESTADO DEL CHAT ---
    const [inputValue, setInputValue] = useState("");
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 1,
            sender: 'bot',
            text: "¡Hola! Soy tu asistente académico. Para ayudarte a encontrar tu camino ideal, necesito conocerte mejor. Cuéntame, ¿qué materias te apasionan en el colegio o qué hobbies tienes?"
        }
    ]);

    // Función para hacer scroll automático al último mensaje
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Manejar el envío de mensajes
    const handleSendMessage = () => {
        if (inputValue.trim() === "") return;

        // 1. Agregar mensaje del usuario
        const newUserMsg: Message = {
            id: Date.now(),
            text: inputValue,
            sender: 'user'
        };

        setMessages(prev => [...prev, newUserMsg]);
        setInputValue(""); // Limpiar input

        // 2. Simular respuesta de la IA (Esto luego se conectará a tu Backend con RAG)
        setTimeout(() => {
            const newBotMsg: Message = {
                id: Date.now() + 1,
                sender: 'bot',
                text: "Entendido. Estoy analizando tus intereses con nuestra base de datos de Universidades del Ecuador... ¿Prefieres una modalidad presencial o virtual?"
            };
            setMessages(prev => [...prev, newBotMsg]);
        }, 1500);
    };

    // Permitir enviar con la tecla Enter
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div className="flex flex-col bg-white min-h-screen">
            
            {/* --- NAVBAR --- */}
            <div className="flex justify-between items-center bg-[#FFFFFFCC] py-4 px-10 sticky top-0 z-50 backdrop-blur-sm shadow-sm">
                {/* Logo */}
                <img
                    src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/549wbqn9_expires_30_days.png"}
                    className="w-[148px] h-[42px] object-contain cursor-pointer"
                    onClick={() => navigate("/")}
                    alt="UniDream Logo"
                />

                {/* Menú Central (Modificado: Inicio en lugar de Nosotros) */}
                <div className="flex-1 flex justify-center items-center gap-12">
                    <span onClick={() => navigate("/")} className={textMenuClass}>
                        {"Inicio"}
                    </span>
                    <span onClick={() => navigate("/carreras")} className={textMenuClass}>
                        {"Carreras"}
                    </span>
                    <span onClick={() => navigate("/universidades")} className={textMenuClass}>
                        {"Universidades"}
                    </span>
                </div>

                {/* Botón Iniciar Sesión */}
                <button 
                    className={`flex items-center gap-2 bg-[#1313EC] py-2.5 px-6 rounded-full border-0 ${buttonPressEffect}`}
                    style={{ boxShadow: "0px 4px 6px #1313EC33" }}
                    onClick={() => alert("Login presionado")}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    <span className="text-white text-sm font-bold">
                        {"Iniciar Sesión"}
                    </span>
                </button>
            </div>

            {/* --- ÁREA PRINCIPAL (CHAT) --- */}
            <div className="flex-1 flex flex-col items-center py-12 bg-gradient-to-b from-[#AAD5FF] to-[#E7E7F3]">
                
                {/* Título y Subtítulo */}
                <div className="text-center mb-8 px-4">
                    <h1 className="text-gray-900 text-4xl md:text-5xl font-bold mb-4">
                        ¿Cuéntame quién eres y <br/>quién quieres ser?
                    </h1>
                    <p className="text-gray-700 text-lg max-w-2xl mx-auto">
                        Tu compañero inteligente para descubrir el profesional que quieres ser.
                    </p>
                </div>

                {/* --- CONTENEDOR DEL CHAT --- */}
                <div className="flex flex-col w-full max-w-[900px] h-[600px] bg-white rounded-[48px] border border-black overflow-hidden shadow-2xl relative">
                    
                    {/* Ventana de Mensajes */}
                    <div className="flex-1 overflow-y-auto p-8 flex flex-col gap-6">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`flex gap-4 max-w-[80%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                    
                                    {/* Avatar Bot */}
                                    {msg.sender === 'bot' && (
                                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                                            <img src="https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/jh4mpyzd_expires_30_days.png" className="w-8 h-8 object-contain" />
                                        </div>
                                    )}

                                    {/* Burbuja de Texto */}
                                    <div className={`p-4 rounded-2xl text-base leading-relaxed shadow-sm
                                        ${msg.sender === 'user' 
                                            ? 'bg-[#1313EC] text-white rounded-tr-none' 
                                            : 'bg-gray-50 text-gray-800 border border-gray-200 rounded-tl-none'
                                        }`}>
                                        {msg.text}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Área de Input */}
                    <div className="p-6 bg-white border-t border-gray-100">
                        {/* Sugerencias Rápidas */}
                        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                            {["Me interesan las ciencias", "Quiero estudiar Medicina", "Soy bueno en Matemáticas"].map((suggestion, index) => (
                                <button 
                                    key={index}
                                    onClick={() => setInputValue(suggestion)}
                                    className="whitespace-nowrap px-4 py-2 rounded-full border border-gray-200 text-xs text-gray-600 hover:bg-gray-50 transition-colors"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>

                        {/* Barra de escritura */}
                        <div className="flex items-center bg-gray-50 rounded-full border border-gray-300 px-2 py-2 shadow-inner focus-within:ring-2 focus-within:ring-blue-200 transition-all">
                            <input
                                type="text"
                                className="flex-1 bg-transparent border-none outline-none px-4 text-gray-700 placeholder-gray-400"
                                placeholder="Escribe aquí tu consulta..."
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />
                            <button 
                                className={`bg-[#1313EC] text-white px-6 py-3 rounded-full font-bold shadow-md hover:bg-[#0f0fb5] transition-colors ${buttonPressEffect}`}
                                onClick={handleSendMessage}
                            >
                                Preguntar
                            </button>
                        </div>
                    </div>

                </div>
            </div>

            {/* --- FOOTER BLANCO --- */}
            <div className="bg-white py-16 px-20 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-20 text-[#0D0D1B]">
                    
                    {/* Columna 1 */}
                    <div className="col-span-1 flex flex-col gap-6">
                        <img
                            src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/w9hmg2ml_expires_30_days.png"}
                            className="w-48 object-contain filter invert opacity-80" // Invertido para que se vea si el logo original era blanco, o ajustado
                            alt="UniDream Logo"
                        />
                        {/* Nota: Si el logo original es blanco puro, necesitarás una versión oscura. 
                            He añadido un filtro por si acaso, pero idealmente usa el logo oscuro aquí */}
                        <p className="text-gray-600 text-sm leading-relaxed">
                            {"Somos un equipo apasionado de estudiantes y desarrolladores comprometidos con democratizar el acceso a la orientación profesional de calidad mediante el uso responsable de la Inteligencia Artificial."}
                        </p>
                    </div>

                    {/* Columna 2 */}
                    <div className="col-span-1 flex flex-col gap-4">
                        <h4 className="text-lg font-bold mb-2 text-[#0D0D1B]">Plataforma</h4>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer" onClick={() => navigate("/carreras")}>Directorio de Carreras</span>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer" onClick={() => navigate("/universidades")}>Ranking de Universidades</span>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer">Datos 100% enfocados en el país</span>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer">Test Vocacional IA</span>
                    </div>

                    {/* Columna 3 (Vacía) */}
                    <div className="col-span-1"></div>

                    {/* Columna 4 */}
                    <div className="col-span-1 flex flex-col gap-4">
                        <h4 className="text-lg font-bold mb-2 text-[#0D0D1B]">Suscríbete</h4>
                        <p className="text-gray-600 text-sm mb-4">
                            Recibe las últimas noticias sobre admisiones y nuevas carreras.
                        </p>
                        <div className="flex flex-col gap-3">
                            <input 
                                type="email" 
                                placeholder="Tu correo electrónico"
                                className="bg-gray-100 text-[#0D0D1B] p-3 rounded-full border border-gray-300 outline-none focus:border-[#1313EC] transition-colors placeholder-gray-500"
                            />
                            <button 
                                className={`bg-[#1313EC] text-white py-3 rounded-full font-bold hover:bg-[#0f0fb5] transition-colors ${buttonPressEffect}`}
                                onClick={() => alert("Suscrito!")}
                            >
                                Suscribirme
                            </button>
                        </div>
                    </div>
                </div>

                {/* Copyright */}
                <div className="border-t border-gray-200 pt-8 text-center">
                    <span className="text-gray-500 text-sm">
                        {"© 2026 UniDream Platform. Todos los derechos reservados. Diseñado para el éxito estudiantil."}
                    </span>
                </div>
            </div>
        </div>
    )
}