export interface ApplicantRequest {
  customer_age: number
  customer_income: number
  home_ownership: 'RENT' | 'OWN' | 'MORTGAGE' | 'OTHER'
  employment_duration: number
  loan_intent: 'EDUCATION' | 'MEDICAL' | 'VENTURE' | 'PERSONAL' | 'DEBTCONSOLIDATION' | 'HOMEIMPROVEMENT'
  loan_grade: 'A' | 'B' | 'C' | 'D' | 'E'
  loan_amnt: number
  loan_int_rate: number
  term_years: number
  cred_hist_length: number
}
export interface ExplanationFactor { feature: string; impact: number }
export interface PredictionResponse {
  default_probability: number
  no_default_probability: number
  decision_threshold: number
  prediction: 'DEFAULT' | 'NO DEFAULT'
  top_risk_factors: ExplanationFactor[]
  top_protective_factors: ExplanationFactor[]
}
