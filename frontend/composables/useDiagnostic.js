export const useDiagnostic = () => {
  const step = useState("diagnostic-step", () => 0);
  const questions = useState("diagnostic-questions", () => []);

  const prospectInfo = useState("prospect-info", () => ({
    empresa: "",
    email: "",
    sector: "",
    facturacion: "",
    numEmpleados: "",
    nombreContacto: "",
    telefono: "",
    cargo: "",
    ciudad: "",
  }));

  const responses = useState("diagnostic-responses", () => ({}));
  const otherText = useState("other-text", () => "");

  const result = useState("diagnostic-result", () => null);
  const loading = useState("diagnostic-loading", () => false);
  const error = useState("diagnostic-error", () => null);

  const loadQuestions = async () => {
    try {
      loading.value = true;
      error.value = null;

      const config = useRuntimeConfig();
      const response = await $fetch(`${config.public.apiBase}/questions`);

      if (response.success) {
        questions.value = response.questions;

        // Inicializar arrays para preguntas multi-select
        questions.value.forEach((q) => {
          if (q.type === "multi-select" && !responses.value[q.id]) {
            responses.value[q.id] = [];
          }
        });

        console.log(`✅ ${response.questions.length} preguntas cargadas`);
      }
    } catch (err) {
      error.value = "Error cargando preguntas: " + err.message;
      console.error("[loadQuestions ERROR]", err);
    } finally {
      loading.value = false;
    }
  };

  const isStep1Valid = computed(() => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return (
      prospectInfo.value.empresa.trim() !== "" &&
      prospectInfo.value.email.trim() !== "" &&
      emailRegex.test(prospectInfo.value.email) &&
      prospectInfo.value.sector !== "" &&
      prospectInfo.value.facturacion !== "" &&
      prospectInfo.value.numEmpleados !== "" &&
      prospectInfo.value.nombreContacto.trim() !== "" &&
      prospectInfo.value.telefono.trim() !== "" &&
      prospectInfo.value.cargo !== "" &&
      prospectInfo.value.ciudad.trim() !== ""
    );
  });

  const isStep2Valid = computed(() => {
    if (!questions.value || questions.value.length === 0) return false;

    const allAnswered = questions.value.every((question) => {
      const answer = responses.value[question.id];

      if (question.type === "multi-select") {
        return Array.isArray(answer) && answer.length > 0;
      }

      return answer !== undefined && answer !== null && answer !== "";
    });

    // Validación especial para Q12 con campo "Otro"
    const q12Question = questions.value.find((q) => q.id === "Q12");
    if (q12Question && q12Question.has_other) {
      const lastOption = q12Question.options[q12Question.options.length - 1];
      if (responses.value.Q12 === lastOption) {
        return allAnswered && otherText.value.trim() !== "";
      }
    }

    return allAnswered;
  });

  const progress = computed(() => {
    const totalQuestions = questions.value.length;
    if (totalQuestions === 0) return 0;

    const answered = questions.value.filter((question) => {
      const answer = responses.value[question.id];
      if (question.type === "multi-select") {
        return Array.isArray(answer) && answer.length > 0;
      }
      return answer !== undefined && answer !== null && answer !== "";
    }).length;

    return Math.round((answered / totalQuestions) * 100);
  });

  const nextStep = () => {
    if (step.value === 0 && isStep1Valid.value) {
      step.value = 1;
    } else if (step.value === 1 && isStep2Valid.value) {
      step.value = 2;
    }
  };

  const prevStep = () => {
    if (step.value > 0) {
      step.value--;
      error.value = null;
    }
  };

  const submitDiagnostic = async () => {
    try {
      loading.value = true;
      error.value = null;
      step.value = 2;

      const config = useRuntimeConfig();

      const payload = {
        nombre_empresa: prospectInfo.value.empresa,
        sector: prospectInfo.value.sector,
        facturacion_rango: prospectInfo.value.facturacion,
        empleados_rango: prospectInfo.value.numEmpleados,
        contacto_nombre: prospectInfo.value.nombreContacto,
        contacto_email: prospectInfo.value.email,
        contacto_telefono: prospectInfo.value.telefono,
        cargo: prospectInfo.value.cargo,
        ciudad: prospectInfo.value.ciudad,

        Q4: responses.value.Q4 || [],
        Q5: responses.value.Q5 || "",
        Q6: responses.value.Q6 || "",
        Q7: responses.value.Q7 || "",
        Q8: responses.value.Q8 || "",
        Q9: responses.value.Q9 || "",
        Q10: responses.value.Q10 || "",
        Q11: responses.value.Q11 || "",
        Q12: responses.value.Q12 || "",
        Q12_otro: otherText.value || "",
        Q13: responses.value.Q13 || "",
        Q14: responses.value.Q14 || "",
        Q15: responses.value.Q15 || "",
      };

      console.log("📤 PAYLOAD ENVIADO:", payload);

      const response = await $fetch(`${config.public.apiBase}/diagnostic`, {
        method: "POST",
        body: payload,
      });

      console.log("✅ RESPUESTA RECIBIDA:", response);

      // ===== LOGS DETALLADOS PARA DEBUG =====
      console.log("📊 STATUS INTEGRACIONES:", {
        sheets_success: response.success,
        diagnostic_id: response.diagnostic_id,
        email_sent: response.email_sent,
        pdf_generated: response.pdf_generated,
        tier: response.tier,
        score: response.score_total,
      });

      if (!response.success) {
        console.warn("⚠️ GOOGLE SHEETS NO GUARDÓ");
        console.warn("   → Revisar logs del backend para detalles");
        console.warn("   → El diagnóstico continuó (PDF y resultados OK)");
      } else {
        console.log("✅ GUARDADO EN GOOGLE SHEETS EXITOSO");
      }

      result.value = response;
    } catch (err) {
      console.error("❌ ERROR EN SUBMIT:", err);

      if (err.status === 429) {
        error.value =
          "Ya procesamos tu diagnóstico recientemente. Por favor espera 5 minutos.";
      } else {
        error.value = err.data?.detail || "Error al procesar diagnóstico";
      }

      console.error("[submitDiagnostic ERROR COMPLETO]", {
        status: err.status,
        message: err.message,
        data: err.data,
      });

      step.value = 1; // Volver al paso anterior
    } finally {
      loading.value = false;
    }
  };

  const reset = () => {
    step.value = 0;
    questions.value = [];
    prospectInfo.value = {
      empresa: "",
      email: "",
      sector: "",
      facturacion: "",
      numEmpleados: "",
      nombreContacto: "",
      telefono: "",
      cargo: "",
      ciudad: "",
    };
    responses.value = {};
    otherText.value = "";
    result.value = null;
    error.value = null;
    loading.value = false;
  };

  return {
    step,
    questions,
    prospectInfo,
    responses,
    otherText,
    result,
    loading,
    error,
    isStep1Valid,
    isStep2Valid,
    progress,
    loadQuestions,
    nextStep,
    prevStep,
    submitDiagnostic,
    reset,
  };
};
