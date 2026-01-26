import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';

const carrerasData = [
    {
        id: 1,
        nombre: "Ingeniería de Software",
        area: "Ingeniería",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/j6deo06v_expires_30_days.png", 
        descripcion: "Diseña y desarrolla sistemas, aplicaciones móviles y soluciones de inteligencia artificial.",
        duracion: "9 Semestres",
        modalidad: "Presencial / Híbrida",
        salarioPromedio: "$1,200 - $2,500 (Junior)",
        universidades: ["Escuela Politécnica Nacional", "Universidad San Francisco", "UDLA"],
        matchIA: 98,
        motivoMatch: "Tu perfil lógico-matemático y gusto por la resolución de problemas encaja perfectamente.",
        url: "https://fis.epn.edu.ec/index.php/carreras/ingenieria-de-software"
    },
    {
        id: 2,
        nombre: "Medicina General",
        area: "Salud",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/3ns51jb1_expires_30_days.png",
        descripcion: "Dedícate al cuidado integral de la salud humana, diagnóstico y prevención de enfermedades.",
        duracion: "12 Semestres",
        modalidad: "Presencial",
        salarioPromedio: "$1,500 - $3,000 (Residente)",
        universidades: ["Universidad Central del Ecuador", "PUCE", "Universidad de Cuenca"],
        matchIA: 0, 
        motivoMatch: "",
        url: "https://www.uce.edu.ec/web/facultad-ciencias-medicas/medicina"
    },
    // ... más datos
    {
        id: 3,
        nombre: "Biomedicina",
        area: "Ingeniería", 
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/5igu44ai_expires_30_days.png",
        descripcion: "Fusiona la ingeniería con las ciencias biológicas para crear dispositivos médicos innovadores.",
        duracion: "10 Semestres",
        modalidad: "Presencial",
        salarioPromedio: "$1,800 - $3,500",
        universidades: ["Yachay Tech", "ESPOL"],
        matchIA: 92,
        motivoMatch: "Tu interés en biología combinado con tecnología te hace un candidato ideal.",
        url: "https://www.yachaytech.edu.ec/academica/escuelas/ciencias-biologicas-ingenieria/biomedicina/"
    },
    {
        id: 4,
        nombre: "Enfermería",
        area: "Salud",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/lm8pte27_expires_30_days.png",
        descripcion: "Cuidado y atención directa a pacientes, gestión de servicios de salud y promoción del bienestar.",
        duracion: "9 Semestres",
        modalidad: "Presencial",
        salarioPromedio: "$900 - $1,500",
        universidades: ["Universidad de Guayaquil", "Universidad Técnica del Norte"],
        matchIA: 75,
        motivoMatch: "Tienes una alta vocación de servicio, aunque tus intereses técnicos son mayores.",
        url: "https://ug.edu.ec/carrera-enfermeria"
    },
    {
        id: 5,
        nombre: "Marketing Digital",
        area: "Negocios",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/ez5q9ye5_expires_30_days.png",
        descripcion: "Domina estrategias de mercado online, SEO, SEM y análisis de datos de consumidores.",
        duracion: "8 Semestres",
        modalidad: "Online / Presencial",
        salarioPromedio: "$800 - $1,800",
        universidades: ["UEES", "Universidad del Azuay"],
        matchIA: 88,
        motivoMatch: "Tu creatividad y capacidad analítica son un buen balance para esta carrera.",
        url: "https://uees.edu.ec/facultades/economia-y-negocios/marketing"
    }
];

export default () => {
    const navigate = useNavigate();
    const [filtroActivo, setFiltroActivo] = useState<"IA" | "Todas" | "Ingeniería" | "Salud">("IA");
    const [busqueda, setBusqueda] = useState("");
    const [carreraSeleccionada, setCarreraSeleccionada] = useState<any>(null); 

    // Menú: font-medium
    const textMenuClass = "text-[#0D0D1B] text-sm transition-colors duration-300 hover:text-[#1213ed] active:text-[#1213ed] cursor-pointer font-medium";
    const buttonPressEffect = "transition-transform duration-100 active:scale-95";

    const carrerasFiltradas = carrerasData.filter(carrera => {
        const coincideBusqueda = carrera.nombre.toLowerCase().includes(busqueda.toLowerCase());
        let coincideCategoria = true;
        if (filtroActivo === "IA") {
            coincideCategoria = carrera.matchIA > 0;
        } else if (filtroActivo === "Todas") {
            coincideCategoria = true;
        } else {
            coincideCategoria = carrera.area === filtroActivo;
        }
        return coincideBusqueda && coincideCategoria;
    });

    if (filtroActivo === "IA") {
        carrerasFiltradas.sort((a, b) => b.matchIA - a.matchIA);
    }

    return (
        <div className="flex flex-col bg-white min-h-screen relative">
            
            {/* --- NAVBAR --- */}
            <div className="flex justify-between items-center bg-[#FFFFFFCC] py-4 px-10 sticky top-0 z-40 backdrop-blur-sm shadow-sm">
                <img
                    src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/549wbqn9_expires_30_days.png"}
                    className="w-[148px] h-[42px] object-contain cursor-pointer"
                    onClick={() => navigate("/")}
                    alt="UniDream Logo"
                />
                <div className="flex-1 flex justify-center items-center gap-12">
                    <span onClick={() => navigate("/")} className={textMenuClass}>Inicio</span>
                    {/* Botón activo: font-bold */}
                    <span onClick={() => navigate("/carreras")} className={`${textMenuClass} text-[#1313EC] font-bold`}>Carreras</span>
                    <span onClick={() => navigate("/universidades")} className={textMenuClass}>Universidades</span>
                </div>
                <button 
                    className={`flex items-center gap-2 bg-[#1313EC] py-2.5 px-6 rounded-full border-0 ${buttonPressEffect}`}
                    style={{ boxShadow: "0px 4px 6px #1313EC33" }}
                    onClick={() => navigate("/asistente")}
                >
                    <span className="text-white text-sm font-bold">Asistente IA</span>
                </button>
            </div>

            {/* --- HEADER --- */}
            <div className="flex flex-col self-stretch max-w-[1152px] mb-8 mx-auto gap-8 mt-10 px-4">
                <div className="flex flex-col md:flex-row justify-between items-end gap-6">
                    <div className="flex flex-col items-start gap-4">
                        {/* Título: font-black */}
                        <span className="text-[#0D0D1B] text-5xl font-black">Explora Carreras Universitarias</span>
                        <span className="text-[#4C4C9A] text-lg max-w-[651px] font-normal">
                            Utiliza nuestra inteligencia artificial para encontrar la carrera que mejor se adapta a tus pasiones y metas profesionales.
                        </span>
                    </div>
                    
                    <div className="relative w-full md:w-96">
                        <input 
                            type="text" 
                            placeholder="Buscar carrera (ej: Medicina, Derecho)..." 
                            className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:border-[#1313EC] transition-colors font-normal"
                            value={busqueda}
                            onChange={(e) => setBusqueda(e.target.value)}
                        />
                        <svg className="w-5 h-5 text-gray-400 absolute left-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    </div>
                </div>

                <div className="flex items-center gap-4 overflow-x-auto pb-2">
                    {/* Botones: font-bold */}
                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'IA' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("IA")}
                    >
                        <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/16w66z7y_expires_30_days.png"} className="w-3.5 h-5 object-contain filter brightness-0 invert" style={{ filter: filtroActivo === 'IA' ? 'brightness(0) invert(1)' : 'none' }} />
                        <span className="text-sm font-bold">Recomendadas por IA</span>
                    </button>

                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'Todas' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("Todas")}
                    >
                        <span className="text-sm font-bold">Todas</span>
                    </button>

                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'Ingeniería' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("Ingeniería")}
                    >
                         <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/il8iu3gh_expires_30_days.png"} className={`w-3.5 h-5 object-contain ${filtroActivo === 'Ingeniería' ? 'brightness-0 invert' : ''}`} />
                        <span className="text-sm font-bold">Ingeniería</span>
                    </button>

                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'Salud' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("Salud")}
                    >
                         <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/3ns51jb1_expires_30_days.png"} className={`w-3.5 h-5 object-contain ${filtroActivo === 'Salud' ? 'brightness-0 invert' : ''}`} />
                        <span className="text-sm font-bold">Salud</span>
                    </button>
                </div>
            </div>

            {/* --- LISTA DE RESULTADOS --- */}
            <div className="flex flex-col self-stretch max-w-[1152px] mx-auto gap-6 mb-20 px-4 min-h-[400px]">
                
                {carrerasFiltradas.length > 0 ? (
                    carrerasFiltradas.map((carrera) => (
                        <div key={carrera.id} className="flex flex-col md:flex-row items-center bg-[#F6F9FA] p-8 gap-8 rounded-[48px] hover:shadow-lg transition-shadow duration-300">
                            
                            <div className="w-32 h-32 rounded-[32px] bg-white flex items-center justify-center shadow-sm shrink-0">
                                <img src={carrera.imagen} className="w-16 h-16 object-contain" alt={carrera.nombre}/>
                            </div>
                            
                            <div className="flex flex-1 flex-col gap-2 w-full">
                                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                                    <h3 className="text-[#0D0D1B] text-2xl font-bold">{carrera.nombre}</h3>
                                    
                                    {filtroActivo === "IA" && (
                                        <div className="bg-[#1313EC1A] text-[#1313EC] px-3 py-1 rounded-full text-xs font-bold border border-[#1313EC33]">
                                            {carrera.matchIA}% AI MATCH
                                        </div>
                                    )}
                                </div>
                                
                                <div className="flex flex-col gap-1">
                                    <div className="flex items-center gap-2">
                                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-md font-bold uppercase">{carrera.area}</span>
                                        <span className="text-[#4C4C9A] text-sm font-medium">• {carrera.duracion}</span>
                                    </div>
                                </div>

                                <p className="text-[#4C4C9A] text-sm leading-relaxed max-w-2xl mt-2 font-normal">
                                    {carrera.descripcion}
                                </p>
                            </div>

                            <div className="flex flex-col gap-3 shrink-0 w-full md:w-auto">
                                <button 
                                    className={`bg-[#1313EC] text-white py-3 px-8 rounded-full font-bold hover:bg-[#0f0fb5] transition-colors ${buttonPressEffect}`}
                                    onClick={() => setCarreraSeleccionada(carrera)}
                                >
                                    Ver Detalles
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <div className="bg-gray-100 p-6 rounded-full mb-4">
                            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">No encontramos esa carrera</h3>
                        <p className="text-gray-500 mt-2 font-normal">Prueba buscando en "Todas" o revisa la ortografía.</p>
                    </div>
                )}
            </div>

            {/* --- FOOTER --- */}
            <div className="bg-white py-16 px-20 border-t border-gray-200 mt-auto">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-20 text-[#0D0D1B]">
                    <div className="col-span-1 flex flex-col gap-6">
                        <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/w9hmg2ml_expires_30_days.png"} className="w-48 object-contain filter invert opacity-80" alt="UniDream Logo"/>
                        <p className="text-gray-600 text-sm leading-relaxed font-normal">Somos un equipo apasionado de estudiantes y desarrolladores comprometidos con democratizar el acceso a la orientación profesional.</p>
                    </div>
                    <div className="col-span-1 flex flex-col gap-4">
                        <h4 className="text-lg font-bold mb-2 text-[#0D0D1B]">Plataforma</h4>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer font-normal" onClick={() => navigate("/carreras")}>Directorio de Carreras</span>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer font-normal" onClick={() => navigate("/universidades")}>Ranking de Universidades</span>
                        <span className="text-gray-600 text-sm hover:text-[#1313EC] cursor-pointer font-normal">Test Vocacional IA</span>
                    </div>
                    <div className="col-span-1"></div>
                    <div className="col-span-1 flex flex-col gap-4">
                        <h4 className="text-lg font-bold mb-2 text-[#0D0D1B]">Suscríbete</h4>
                        <div className="flex flex-col gap-3">
                            <input type="email" placeholder="Tu correo electrónico" className="bg-gray-100 text-[#0D0D1B] p-3 rounded-full border border-gray-300 outline-none focus:border-[#1313EC] font-normal" />
                            <button className="bg-[#1313EC] text-white py-3 rounded-full font-bold hover:bg-[#0f0fb5]" onClick={() => alert("Suscrito!")}>Suscribirme</button>
                        </div>
                    </div>
                </div>
                <div className="border-t border-gray-200 pt-8 text-center">
                    <span className="text-gray-500 text-sm font-normal">© 2026 UniDream Platform. Todos los derechos reservados.</span>
                </div>
            </div>

            {/* --- MODAL --- */}
            {carreraSeleccionada && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4">
                    <div className="bg-white rounded-[32px] w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl animate-fade-in-up">
                        <div className="relative h-40 bg-[#1313EC] rounded-t-[32px] flex items-center justify-center">
                            <button 
                                onClick={() => setCarreraSeleccionada(null)}
                                className="absolute top-4 right-4 bg-white/20 hover:bg-white/40 text-white rounded-full p-2 transition-colors"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                            </button>
                            <div className="w-24 h-24 bg-white rounded-3xl flex items-center justify-center border-4 border-white shadow-lg absolute -bottom-12">
                                <img src={carreraSeleccionada.imagen} className="w-14 h-14 object-contain" />
                            </div>
                        </div>

                        <div className="pt-16 pb-8 px-8 flex flex-col gap-6 text-center">
                            <div>
                                <h2 className="text-2xl font-bold text-[#0D0D1B]">{carreraSeleccionada.nombre}</h2>
                                <span className="bg-blue-100 text-[#1313EC] px-3 py-1 rounded-full text-xs font-bold uppercase mt-2 inline-block">
                                    {carreraSeleccionada.area}
                                </span>
                            </div>

                            <p className="text-gray-600 text-sm leading-relaxed font-normal">
                                {carreraSeleccionada.descripcion}
                            </p>

                            <div className="grid grid-cols-2 gap-4 text-left">
                                <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                                    <span className="text-xs text-gray-500 uppercase font-bold">Salario Promedio</span>
                                    <p className="text-[#0D0D1B] font-bold mt-1">{carreraSeleccionada.salarioPromedio}</p>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                                    <span className="text-xs text-gray-500 uppercase font-bold">Duración</span>
                                    <p className="text-[#0D0D1B] font-bold mt-1">{carreraSeleccionada.duracion}</p>
                                </div>
                            </div>

                            {filtroActivo === 'IA' && carreraSeleccionada.matchIA > 0 && (
                                <div className="bg-[#1313EC0D] border border-[#1313EC33] rounded-2xl p-6 text-left">
                                    <h4 className="text-[#1313EC] font-bold mb-2 uppercase text-xs tracking-wider flex items-center gap-2">
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"></path></svg>
                                        Análisis de Compatibilidad
                                    </h4>
                                    <p className="text-[#1313EC] text-sm font-medium mb-1">
                                        Nivel de Match: <span className="font-bold text-lg">{carreraSeleccionada.matchIA}%</span>
                                    </p>
                                    <p className="text-gray-600 text-xs italic font-normal">
                                        "{carreraSeleccionada.motivoMatch}"
                                    </p>
                                </div>
                            )}

                            <div className="text-left">
                                <h4 className="text-[#0D0D1B] font-bold text-sm mb-3">Disponible en estas Universidades:</h4>
                                <div className="flex flex-wrap gap-2">
                                    {carreraSeleccionada.universidades.map((uni: string, idx: number) => (
                                        <span key={idx} className="bg-white border border-gray-300 px-3 py-1.5 rounded-full text-xs text-gray-700 font-medium hover:border-[#1313EC] hover:text-[#1313EC] cursor-pointer transition-colors"
                                            onClick={() => navigate("/universidades")} 
                                        >
                                            {uni}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            
                            <a 
                                href={carreraSeleccionada.url} 
                                target="_blank" 
                                className="bg-[#1313EC] text-white py-4 rounded-xl font-bold hover:bg-[#0f0fb5] transition-colors w-full mt-4 block"
                            >
                                Ver Malla Curricular Oficial
                            </a>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}