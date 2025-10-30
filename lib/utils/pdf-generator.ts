// ============================================================================
// PDF GENERATOR - Generate loan sanction letters
// ============================================================================

import PDFDocument from 'pdfkit';
import { SanctionLetterData } from '@/types';
import { formatCurrency, formatPercentage, calculateTotalInterest } from './calculations';

/**
 * Generate a professional loan sanction letter PDF
 * Returns a Buffer that can be sent as HTTP response
 */
export async function generateSanctionLetter(
  data: SanctionLetterData
): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument({
        size: 'A4',
        margins: { top: 50, bottom: 50, left: 50, right: 50 },
      });

      const chunks: Buffer[] = [];

      doc.on('data', (chunk) => chunks.push(chunk));
      doc.on('end', () => resolve(Buffer.concat(chunks)));
      doc.on('error', reject);

      // ========== Header ==========
      doc
        .fontSize(20)
        .font('Helvetica-Bold')
        .text('QuickLoan Finance Pvt. Ltd.', { align: 'center' })
        .fontSize(10)
        .font('Helvetica')
        .text('Registered Office: 123 Financial District, Mumbai - 400001', {
          align: 'center',
        })
        .text('CIN: U65999MH2020PTC123456 | Website: www.quickloan.com', {
          align: 'center',
        })
        .moveDown(2);

      // ========== Title ==========
      doc
        .fontSize(16)
        .font('Helvetica-Bold')
        .fillColor('#2563eb')
        .text('LOAN SANCTION LETTER', { align: 'center' })
        .fillColor('#000000')
        .moveDown(1);

      // ========== Letter Details ==========
      const letterDate = new Date(data.date).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
      });

      doc
        .fontSize(10)
        .font('Helvetica')
        .text(`Letter No: ${data.application_id}`, { align: 'right' })
        .text(`Date: ${letterDate}`, { align: 'right' })
        .moveDown(1.5);

      // ========== Customer Details ==========
      doc
        .fontSize(11)
        .font('Helvetica-Bold')
        .text('To,')
        .font('Helvetica')
        .text(data.customer_name)
        .text(`PAN: ${data.pan_number}`)
        .text(`Phone: ${data.phone}`)
        .moveDown(1.5);

      // ========== Greeting ==========
      doc
        .fontSize(11)
        .font('Helvetica-Bold')
        .text(`Dear ${data.customer_name.split(' ')[0]},`)
        .moveDown(0.5);

      doc
        .font('Helvetica')
        .text(
          'We are pleased to inform you that your personal loan application has been approved. The details of your loan sanction are as follows:',
          { align: 'justify' }
        )
        .moveDown(1);

      // ========== Loan Details Table ==========
      const leftColumn = 80;
      const rightColumn = 300;
      let yPosition = doc.y;

      // Draw box
      doc
        .rect(50, yPosition - 10, 495, 180)
        .fillOpacity(0.95)
        .fillAndStroke('#f1f5f9', '#cbd5e1');

      doc.fillOpacity(1).fillColor('#000000');

      yPosition = doc.y;

      const addRow = (label: string, value: string, isBold = false) => {
        doc
          .fontSize(11)
          .font('Helvetica-Bold')
          .text(label, leftColumn, yPosition);
        
        doc
          .font(isBold ? 'Helvetica-Bold' : 'Helvetica')
          .text(value, rightColumn, yPosition);
        
        yPosition += 25;
      };

      addRow('Sanctioned Amount:', formatCurrency(data.sanctioned_amount), true);
      addRow('Interest Rate:', formatPercentage(data.interest_rate, 2) + ' per annum');
      addRow('Loan Tenure:', `${data.tenure} months`);
      addRow('Monthly EMI:', formatCurrency(data.monthly_emi), true);
      addRow('Processing Fee:', formatCurrency(data.processing_fee));

      const totalInterest = calculateTotalInterest(
        data.sanctioned_amount,
        data.monthly_emi,
        data.tenure
      );
      addRow('Total Interest:', formatCurrency(totalInterest));

      const totalPayable = data.sanctioned_amount + totalInterest + data.processing_fee;
      addRow('Total Amount Payable:', formatCurrency(totalPayable), true);

      doc.y = yPosition + 10;
      doc.moveDown(1);

      // ========== Terms & Conditions ==========
      doc
        .fontSize(12)
        .font('Helvetica-Bold')
        .text('Terms & Conditions:')
        .moveDown(0.5);

      const terms = [
        'This sanction is valid for 30 days from the date of issue.',
        'The loan will be disbursed upon submission of all required documents.',
        'EMI payments must be made on or before the 5th of every month.',
        'Processing fee is non-refundable and will be deducted from the sanctioned amount.',
        'Late payment charges of 2% per month will apply on overdue EMIs.',
        'The loan is subject to verification of all documents and information provided.',
        'The borrower must maintain adequate insurance coverage during the loan tenure.',
        'Prepayment is allowed after 6 EMIs with a prepayment charge of 2%.',
      ];

      doc.fontSize(9).font('Helvetica').list(terms, {
        bulletRadius: 2,
        textIndent: 20,
        lineGap: 5,
      });

      doc.moveDown(1.5);

      // ========== Next Steps ==========
      doc
        .fontSize(11)
        .font('Helvetica-Bold')
        .text('Next Steps:')
        .moveDown(0.5);

      doc
        .fontSize(10)
        .font('Helvetica')
        .text('1. Review and accept the terms and conditions', { indent: 20 })
        .text('2. Submit the following documents:', { indent: 20 })
        .text('   • Last 3 months salary slips', { indent: 35 })
        .text('   • Last 6 months bank statements', { indent: 35 })
        .text('   • Address proof', { indent: 35 })
        .text('3. E-sign the loan agreement', { indent: 20 })
        .text('4. Loan will be disbursed within 24 hours', { indent: 20 })
        .moveDown(2);

      // ========== Closing ==========
      doc
        .fontSize(10)
        .font('Helvetica')
        .text(
          'Congratulations on your loan approval! We look forward to serving you.',
          { align: 'justify' }
        )
        .moveDown(1);

      doc.text('For any queries, please contact us at:').moveDown(0.3);
      doc
        .text('Email: support@quickloan.com')
        .text('Phone: 1800-123-4567')
        .text('Timings: 9:00 AM - 6:00 PM (Mon-Sat)')
        .moveDown(2);

      // ========== Signature ==========
      doc
        .fontSize(10)
        .font('Helvetica-Bold')
        .text('Warm regards,')
        .moveDown(0.5)
        .text('QuickLoan Credit Team')
        .font('Helvetica')
        .fontSize(9)
        .text('This is a system-generated letter and does not require a signature.')
        .moveDown(1);

      // ========== Footer ==========
      const pageHeight = doc.page.height;
      doc
        .fontSize(8)
        .font('Helvetica')
        .text(
          'This sanction letter is confidential and intended solely for the addressee.',
          50,
          pageHeight - 70,
          { align: 'center', width: 495 }
        )
        .text(
          '© 2025 QuickLoan Finance Pvt. Ltd. All rights reserved.',
          50,
          pageHeight - 55,
          { align: 'center', width: 495 }
        );

      // Finalize PDF
      doc.end();
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Generate filename for sanction letter
 */
export function generateSanctionLetterFilename(
  applicationId: string,
  customerName: string
): string {
  const sanitizedName = customerName.replace(/[^a-zA-Z0-9]/g, '_');
  const timestamp = Date.now();
  return `Sanction_Letter_${applicationId}_${sanitizedName}_${timestamp}.pdf`;
}