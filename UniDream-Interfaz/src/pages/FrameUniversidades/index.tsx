import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';

const universidadesData = [
    {
        id: 1,
        nombre: "Universidad Nacional de Tecnología",
        tipo: "Publica",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/qyxjr5s3_expires_30_days.png",
        ubicacion: "Quito, Pichincha",
        descripcion: "Líder en investigación tecnológica con más de 45 programas de ingeniería y convenios internacionales.",
        matchIA: 98,
        carreraSugeridaIA: "Ingeniería de Software",
        facultades: ["Ingeniería", "Ciencias Exactas", "Mecatrónica"],
        url: "https://www.epn.edu.ec"
    },
    {
        id: 2,
        nombre: "Instituto de Artes y Ciencias",
        tipo: "Privada",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/e7larkph_expires_30_days.png",
        ubicacion: "Guayaquil, Guayas",
        descripcion: "Enfocado en el desarrollo creativo y pensamiento crítico. Ofrece programas exclusivos en Diseño.",
        matchIA: 85,
        carreraSugeridaIA: "Diseño Gráfico",
        facultades: ["Artes", "Arquitectura", "Humanidades"],
        url: "https://www.uartes.edu.ec"
    },
    {
        id: 3,
        nombre: "Universidad Metropolitana de Innovación",
        tipo: "Privada",
        imagen: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/aw1r5zfw_expires_30_days.png",
        ubicacion: "Cuenca, Azuay",
        descripcion: "Pioneros en el modelo educativo de aprendizaje basado en retos. Especialización en negocios.",
        matchIA: 70,
        carreraSugeridaIA: "Administración de Empresas",
        facultades: ["Negocios", "Economía", "Marketing"],
        url: "https://www.uda.edu.ec"
    }
];

export default () => {
    const navigate = useNavigate();
    const [filtroActivo, setFiltroActivo] = useState<"IA" | "Publica" | "Privada">("IA");
    const [busqueda, setBusqueda] = useState("");
    const [universidadSeleccionada, setUniversidadSeleccionada] = useState<any>(null);

    // Menú: font-medium
    const textMenuClass = "text-[#0D0D1B] text-sm transition-colors duration-300 hover:text-[#1213ed] active:text-[#1213ed] cursor-pointer font-medium";
    const buttonPressEffect = "transition-transform duration-100 active:scale-95";

    const universidadesFiltradas = universidadesData.filter(uni => {
        const coincideBusqueda = uni.nombre.toLowerCase().includes(busqueda.toLowerCase());
        let coincideCategoria = true;
        if (filtroActivo === "IA") {
            coincideCategoria = true; 
        } else {
            coincideCategoria = uni.tipo === filtroActivo;
        }
        return coincideBusqueda && coincideCategoria;
    });

    if (filtroActivo === "IA") {
        universidadesFiltradas.sort((a, b) => b.matchIA - a.matchIA);
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
                    <span onClick={() => navigate("/carreras")} className={textMenuClass}>Carreras</span>
                    {/* Botón activo: font-bold para resaltar */}
                    <span onClick={() => navigate("/universidades")} className={`${textMenuClass} text-[#1313EC] font-bold`}>Universidades</span>
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
                        {/* Título Principal: font-black */}
                        <span className="text-[#0D0D1B] text-5xl font-black">Explora Universidades</span>
                        <span className="text-[#4C4C9A] text-lg max-w-[628px] font-normal">
                            Utilizamos inteligencia artificial para analizar programas académicos y encontrar la institución que mejor se alinea con tus metas.
                        </span>
                    </div>
                    
                    <div className="relative w-full md:w-96">
                        <input 
                            type="text" 
                            placeholder="Buscar universidad..." 
                            className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:border-[#1313EC] transition-colors font-normal"
                            value={busqueda}
                            onChange={(e) => setBusqueda(e.target.value)}
                        />
                        <svg className="w-5 h-5 text-gray-400 absolute left-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    </div>
                </div>

                <div className="flex items-center gap-4 overflow-x-auto pb-2">
                    {/* Botones filtro: font-medium o font-bold */}
                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'IA' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("IA")}
                    >
                        <img src={"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/y0WLx2RbqX/16w66z7y_expires_30_days.png"} className="w-3.5 h-5 object-contain filter brightness-0 invert" style={{ filter: filtroActivo === 'IA' ? 'brightness(0) invert(1)' : 'none' }} />
                        <span className="text-sm font-bold">Recomendadas por IA</span>
                    </button>

                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'Publica' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("Publica")}
                    >
                        <span className="text-sm font-bold">Públicas</span>
                    </button>

                    <button 
                        className={`flex shrink-0 items-center py-[9px] px-5 gap-2 rounded-full border transition-all ${filtroActivo === 'Privada' ? 'bg-[#1313EC] text-white border-transparent shadow-md' : 'bg-white text-[#0D0D1B] border-[#E7E7F3] hover:bg-gray-50'}`}
                        onClick={() => setFiltroActivo("Privada")}
                    >
                        <span className="text-sm font-bold">Privadas</span>
                    </button>
                </div>
            </div>

            {/* --- LISTA DE RESULTADOS --- */}
            <div className="flex flex-col self-stretch max-w-[1152px] mx-auto gap-6 mb-20 px-4 min-h-[400px]">
                
                {universidadesFiltradas.length > 0 ? (
                    universidadesFiltradas.map((uni) => (
                        <div key={uni.id} className="flex flex-col md:flex-row items-center bg-[#F6F9FA] p-8 gap-8 rounded-[48px] hover:shadow-lg transition-shadow duration-300">
                            <img src={uni.imagen} className="w-32 h-32 rounded-3xl object-cover bg-white shadow-sm" alt={uni.nombre}/>
                            
                            <div className="flex flex-1 flex-col gap-2 w-full">
                                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                                    {/* Nombre Universidad: font-bold */}
                                    <h3 className="text-[#0D0D1B] text-2xl font-bold">{uni.nombre}</h3>
                                    
                                    {filtroActivo === "IA" && (
                                        <div className="bg-[#1313EC1A] text-[#1313EC] px-3 py-1 rounded-full text-xs font-bold border border-[#1313EC33]">
                                            {uni.matchIA}% AI MATCH
                                        </div>
                                    )}
                                </div>
                                
                                <div className="flex flex-col gap-1">
                                    {/* Ubicación: font-medium */}
                                    <span className="text-[#4C4C9A] text-sm font-medium">{uni.ubicacion}</span>
                                    {filtroActivo === "IA" ? (
                                         <span className="text-[#1313EC] text-base font-medium">
                                            Carrera sugerida: <span className="font-bold">{uni.carreraSugeridaIA}</span>
                                         </span>
                                    ) : (
                                        <span className="text-gray-500 text-sm font-normal">
                                            {uni.tipo === "Publica" ? "Institución Pública" : "Institución Privada"}
                                        </span>
                                    )}
                                </div>

                                {/* Descripción: font-normal */}
                                <p className="text-[#4C4C9A] text-sm leading-relaxed max-w-2xl font-normal">
                                    {uni.descripcion}
                                </p>
                            </div>

                            <div className="flex flex-col gap-3 shrink-0 w-full md:w-auto">
                                <button 
                                    className={`bg-[#1313EC] text-white py-3 px-8 rounded-full font-bold hover:bg-[#0f0fb5] transition-colors ${buttonPressEffect}`}
                                    onClick={() => setUniversidadSeleccionada(uni)}
                                >
                                    Ver Detalles
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <div className="bg-gray-100 p-6 rounded-full mb-4">
                            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">Esta universidad no está registrada</h3>
                        <p className="text-gray-500 mt-2 font-normal">Intenta buscar con otro nombre o revisa la ortografía.</p>
                    </div>
                )}

                {universidadesFiltradas.length > 0 && (
                    <div className="flex justify-center mt-8">
                        <button className="flex items-center gap-2 px-6 py-3 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors">
                            <span className="text-[#0D0D1B] font-bold">Cargar más universidades</span>
                        </button>
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
            {universidadSeleccionada && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4">
                    <div className="bg-white rounded-[32px] w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl animate-fade-in-up">
                        <div className="relative h-40 bg-[#1313EC] rounded-t-[32px] flex items-center justify-center">
                            <button 
                                onClick={() => setUniversidadSeleccionada(null)}
                                className="absolute top-4 right-4 bg-white/20 hover:bg-white/40 text-white rounded-full p-2 transition-colors"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                            </button>
                            <img src={universidadSeleccionada.imagen} className="w-24 h-24 rounded-full border-4 border-white object-cover absolute -bottom-12 shadow-lg" />
                        </div>

                        <div className="pt-16 pb-8 px-8 flex flex-col gap-6 text-center">
                            <div>
                                <h2 className="text-2xl font-bold text-[#0D0D1B]">{universidadSeleccionada.nombre}</h2>
                                <span className="text-[#4C4C9A] font-medium">{universidadSeleccionada.ubicacion}</span>
                            </div>

                            <p className="text-gray-600 text-sm leading-relaxed font-normal">
                                {universidadSeleccionada.descripcion}
                            </p>

                            <div className="bg-gray-50 rounded-2xl p-6 text-left">
                                <h4 className="text-[#1313EC] font-bold mb-4 uppercase text-xs tracking-wider">
                                    {filtroActivo === 'IA' ? "Recomendación de Inteligencia Artificial" : "Oferta Académica General"}
                                </h4>
                                
                                {filtroActivo === 'IA' ? (
                                    <div className="flex flex-col gap-2">
                                        <div className="flex items-center justify-between">
                                            <span className="text-gray-700 font-medium">Carrera Ideal:</span>
                                            <span className="font-bold text-[#0D0D1B]">{universidadSeleccionada.carreraSugeridaIA}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-gray-700 font-medium">Compatibilidad:</span>
                                            <span className="text-green-600 font-bold">{universidadSeleccionada.matchIA}% Match</span>
                                        </div>
                                        <p className="text-xs text-gray-500 mt-2 font-normal">La IA ha seleccionado esta carrera basada en tus intereses previos.</p>
                                    </div>
                                ) : (
                                    <div className="flex flex-col gap-2">
                                        <p className="text-sm text-gray-600 mb-2 font-medium">Facultades disponibles:</p>
                                        <div className="flex flex-wrap gap-2">
                                            {universidadSeleccionada.facultades.map((fac: string, idx: number) => (
                                                <span key={idx} className="bg-white border border-gray-200 px-3 py-1 rounded-full text-xs text-gray-700 font-normal">
                                                    {fac}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <a 
                                href={universidadSeleccionada.url} 
                                target="_blank" 
                                className="bg-[#1313EC] text-white py-4 rounded-xl font-bold hover:bg-[#0f0fb5] transition-colors w-full"
                            >
                                Visitar Sitio Web Oficial
                            </a>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}