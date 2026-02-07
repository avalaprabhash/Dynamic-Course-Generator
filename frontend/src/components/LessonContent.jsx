import React from 'react';
import { 
  Clock, Target, Lightbulb, AlertTriangle, CheckCircle, 
  BookOpen, Code, Brain, ArrowRight, MessageCircle, Footprints
} from 'lucide-react';
import BloomBadge from './BloomBadge';

function LessonContent({ lesson }) {
  const content = lesson.content;
  
  // Check if content is structured (object) or legacy (string)
  const isStructured = content && typeof content === 'object' && !Array.isArray(content);
  
  // Render code blocks
  const renderCode = (code) => {
    if (!code) return null;
    return (
      <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto text-sm my-4 border border-slate-700">
        <code>{code}</code>
      </pre>
    );
  };
  
  // Render inline text with bold, italic, code styling
  const renderInlineStyles = (text) => {
    if (!text) return null;
    
    const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g);
    
    return parts.map((part, i) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded text-sm font-mono">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-slate-800">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
        return <em key={i} className="italic">{part.slice(1, -1)}</em>;
      }
      return part;
    });
  };
  
  // Render a text block (handles paragraphs)
  const renderText = (text) => {
    if (!text) return null;
    
    const paragraphs = text.split(/\n\n+/);
    
    return paragraphs.map((para, idx) => (
      <p key={idx} className="mb-3 leading-relaxed text-slate-600">
        {renderInlineStyles(para.trim())}
      </p>
    ));
  };
  
  // Render legacy string content (fallback)
  const renderLegacyContent = (stringContent) => {
    if (!stringContent) return null;
    
    const sections = stringContent.split(/\n\n+/);
    
    return sections.map((section, index) => {
      const trimmed = section.trim();
      
      if (trimmed.startsWith('## ')) {
        return (
          <h2 key={index} className="text-xl font-semibold mt-8 mb-3 text-slate-800 first:mt-0">
            {trimmed.replace('## ', '')}
          </h2>
        );
      }
      
      if (trimmed.startsWith('### ')) {
        return (
          <h3 key={index} className="text-lg font-medium mt-5 mb-2 text-slate-700">
            {trimmed.replace('### ', '')}
          </h3>
        );
      }
      
      if (trimmed.startsWith('```')) {
        const lines = trimmed.split('\n');
        const code = lines.slice(1, -1).join('\n');
        return renderCode(code);
      }
      
      if (/^\d+\.\s/.test(trimmed)) {
        const items = trimmed.split('\n').filter(line => /^\d+\.\s/.test(line.trim()));
        return (
          <ol key={index} className="my-4 space-y-2 list-none">
            {items.map((item, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-slate-200 text-slate-600 rounded-full flex items-center justify-center text-sm font-medium">
                  {i + 1}
                </span>
                <span className="text-slate-600 pt-0.5">{renderInlineStyles(item.replace(/^\d+\.\s/, ''))}</span>
              </li>
            ))}
          </ol>
        );
      }
      
      if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
        const items = trimmed.split('\n').filter(line => 
          line.trim().startsWith('- ') || line.trim().startsWith('• ')
        );
        return (
          <ul key={index} className="my-4 space-y-2">
            {items.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-slate-600">
                <span className="text-slate-400 mt-1.5">•</span>
                <span>{renderInlineStyles(item.replace(/^[-•]\s/, ''))}</span>
              </li>
            ))}
          </ul>
        );
      }
      
      return (
        <p key={index} className="mb-4 leading-relaxed text-slate-600">
          {renderInlineStyles(trimmed)}
        </p>
      );
    });
  };
  
  // Section Header Component
  const SectionHeader = ({ icon: Icon, title }) => (
    <div className="flex items-center gap-2 mb-4 pb-2 border-b border-slate-200">
      <Icon className="w-5 h-5 text-slate-500" />
      <h2 className="text-base font-semibold text-slate-700">{title}</h2>
    </div>
  );
  
  // Render structured content
  const renderStructuredContent = () => {
    return (
      <div className="space-y-6">
        {/* Introduction */}
        <section className="bg-slate-50 p-5 rounded-lg border border-slate-200">
          <SectionHeader icon={Lightbulb} title="Introduction" />
          {renderText(content.introduction)}
        </section>
        
        {/* Lesson Overview */}
        {content.lesson_overview && content.lesson_overview.length > 0 && (
          <section className="bg-white p-5 rounded-lg border border-slate-200">
            <SectionHeader icon={BookOpen} title="What You'll Learn" />
            <ul className="space-y-2">
              {content.lesson_overview.map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <ArrowRight className="w-4 h-4 text-slate-400 mt-1 flex-shrink-0" />
                  <span className="text-slate-600">{renderInlineStyles(item)}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
        
        {/* Core Concepts */}
        {content.core_concepts && content.core_concepts.length > 0 && (
          <section>
            <SectionHeader icon={Brain} title="Core Concepts" />
            <div className="space-y-5">
              {content.core_concepts.map((concept, idx) => (
                <div key={idx} className="border-l-2 border-slate-300 pl-5 py-1">
                  <h3 className="text-base font-medium text-slate-800 mb-3">{concept.title}</h3>
                  {renderText(concept.explanation)}
                  {concept.code_example && renderCode(concept.code_example)}
                </div>
              ))}
            </div>
          </section>
        )}
        
        {/* Guided Walkthrough */}
        {content.guided_walkthrough && content.guided_walkthrough.length > 0 && (
          <section className="bg-slate-50 p-5 rounded-lg border border-slate-200">
            <SectionHeader icon={Footprints} title="Step-by-Step Walkthrough" />
            <ol className="space-y-3">
              {content.guided_walkthrough.map((step, idx) => (
                <li key={idx} className="flex items-start gap-4">
                  <span className="flex-shrink-0 w-7 h-7 bg-slate-700 text-white rounded-full flex items-center justify-center font-medium text-sm">
                    {idx + 1}
                  </span>
                  <div className="pt-1 text-slate-600 flex-1">
                    {renderInlineStyles(step)}
                  </div>
                </li>
              ))}
            </ol>
          </section>
        )}
        
        {/* Practical Examples */}
        {content.practical_examples && content.practical_examples.length > 0 && (
          <section>
            <SectionHeader icon={Code} title="Practical Examples" />
            <div className="space-y-4">
              {content.practical_examples.map((example, idx) => (
                <div key={idx} className="bg-white p-5 rounded-lg border border-slate-200">
                  <h4 className="font-medium text-slate-700 mb-3">
                    Example {idx + 1}: {example.description}
                  </h4>
                  {example.code && renderCode(example.code)}
                  <div className="mt-3 text-slate-600 text-sm">
                    {renderText(example.explanation)}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
        
        {/* Common Pitfalls */}
        {content.common_pitfalls && content.common_pitfalls.length > 0 && (
          <section className="bg-amber-50 p-5 rounded-lg border border-amber-200">
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-amber-200">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <h2 className="text-base font-semibold text-amber-800">Common Pitfalls</h2>
            </div>
            <ul className="space-y-2">
              {content.common_pitfalls.map((pitfall, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="text-amber-500 mt-0.5">•</span>
                  <span className="text-amber-900">{renderInlineStyles(pitfall)}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
        
        {/* Mental Model */}
        {content.mental_model && (
          <section className="bg-slate-100 p-5 rounded-lg border border-slate-200">
            <SectionHeader icon={Brain} title="Mental Model" />
            <div className="text-slate-600 italic">
              {renderText(content.mental_model)}
            </div>
          </section>
        )}
        
        {/* Summary */}
        {content.summary && (
          <section className="bg-emerald-50 p-5 rounded-lg border border-emerald-200">
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-emerald-200">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <h2 className="text-base font-semibold text-emerald-800">Summary</h2>
            </div>
            <div className="text-emerald-900">
              {renderText(content.summary)}
            </div>
          </section>
        )}
        
        {/* Further Thinking */}
        {content.further_thinking && content.further_thinking.length > 0 && (
          <section className="bg-white p-5 rounded-lg border border-slate-200">
            <SectionHeader icon={MessageCircle} title="Further Thinking" />
            <ul className="space-y-2">
              {content.further_thinking.map((prompt, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="text-slate-500 font-medium">{idx + 1}.</span>
                  <span className="text-slate-600">{renderInlineStyles(prompt)}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    );
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-200">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <BloomBadge level={lesson.bloom_level} showDescription />
          <span className="flex items-center gap-1.5 text-sm text-slate-500">
            <Clock className="w-4 h-4" />
            {lesson.estimated_duration_minutes} min
          </span>
        </div>
        
        <h1 className="text-2xl font-bold text-slate-900">
          {lesson.lesson_title}
        </h1>
      </div>
      
      {/* Learning Outcomes */}
      <div className="p-6 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-2 mb-3">
          <Target className="w-5 h-5 text-slate-600" />
          <h2 className="font-semibold text-slate-700">Learning Outcomes</h2>
        </div>
        <ul className="space-y-2">
          {lesson.learning_outcomes.map((outcome, index) => (
            <li key={index} className="flex items-start gap-2 text-slate-600">
              <span className="text-slate-400 font-bold mt-0.5">•</span>
              {outcome}
            </li>
          ))}
        </ul>
      </div>
      
      {/* Content */}
      <div className="p-6 lesson-content">
        {isStructured ? renderStructuredContent() : renderLegacyContent(content)}
      </div>
    </div>
  );
}

export default LessonContent;
