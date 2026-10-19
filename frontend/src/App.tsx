import { useState } from "react";

type ApplicantForm = {
  customer_age: number;
  customer_income: number;
  home_ownership: "RENT" | "OWN" | "MORTGAGE" | "OTHER";
  employment_duration: number;
  loan_intent:
    | "EDUCATION"
    | "MEDICAL"
    | "VENTURE"
    | "PERSONAL"
    | "DEBTCONSOLIDATION"
    | "HOMEIMPROVEMENT";
  loan_grade: "A" | "B" | "C" | "D" | "E";
  loan_amnt: number;
  loan_int_rate: number;
  term_years: number;
  cred_hist_length: number;
};

function App() {
  const [formData, setFormData] = useState<ApplicantForm>({
    customer_age: 30,
    customer_income: 50000,
    home_ownership: "RENT",
    employment_duration: 5,
    loan_intent: "PERSONAL",
    loan_grade: "B",
    loan_amnt: 10000,
    loan_int_rate: 8,
    term_years: 2,
    cred_hist_length: 5,
  });

  function handleChange(
    event:
      | React.ChangeEvent<HTMLInputElement>
      | React.ChangeEvent<HTMLSelectElement>
  ) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]:
        event.target.type === "number"
          ? Number(value)
          : value,
    }));
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    console.log(formData);
  }

  return (
    <main>
      <h1>Loan Risk Assessment</h1>

      <form onSubmit={handleSubmit}>
        <label>
          Customer Age
          <input
            type="number"
            name="customer_age"
            value={formData.customer_age}
            onChange={handleChange}
          />
        </label>

        <label>
          Customer Income
          <input
            type="number"
            name="customer_income"
            value={formData.customer_income}
            onChange={handleChange}
          />
        </label>

        <label>
          Home Ownership
          <select
            name="home_ownership"
            value={formData.home_ownership}
            onChange={handleChange}
          >
            <option value="RENT">Rent</option>
            <option value="OWN">Own</option>
            <option value="MORTGAGE">Mortgage</option>
            <option value="OTHER">Other</option>
          </select>
        </label>

        <label>
          Employment Duration
          <input
            type="number"
            name="employment_duration"
            value={formData.employment_duration}
            onChange={handleChange}
          />
        </label>

        <label>
          Loan Purpose
          <select
            name="loan_intent"
            value={formData.loan_intent}
            onChange={handleChange}
          >
            <option value="EDUCATION">Education</option>
            <option value="MEDICAL">Medical</option>
            <option value="VENTURE">Venture</option>
            <option value="PERSONAL">Personal</option>
            <option value="DEBTCONSOLIDATION">
              Debt Consolidation
            </option>
            <option value="HOMEIMPROVEMENT">
              Home Improvement
            </option>
          </select>
        </label>

        <label>
          Loan Grade
          <select
            name="loan_grade"
            value={formData.loan_grade}
            onChange={handleChange}
          >
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="D">D</option>
            <option value="E">E</option>
          </select>
        </label>

        <label>
          Loan Amount
          <input
            type="number"
            name="loan_amnt"
            value={formData.loan_amnt}
            onChange={handleChange}
          />
        </label>

        <label>
          Interest Rate
          <input
            type="number"
            name="loan_int_rate"
            value={formData.loan_int_rate}
            onChange={handleChange}
          />
        </label>

        <label>
          Loan Term
          <input
            type="number"
            name="term_years"
            value={formData.term_years}
            onChange={handleChange}
          />
        </label>

        <label>
          Credit History Length
          <input
            type="number"
            name="cred_hist_length"
            value={formData.cred_hist_length}
            onChange={handleChange}
          />
        </label>

        <button type="submit">
          Assess Risk
        </button>
      </form>
    </main>
  );
}

export default App;